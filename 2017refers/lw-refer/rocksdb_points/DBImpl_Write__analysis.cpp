// RocksDB写入数据过程DBImpl::Write()源代码分析

Status DBImpl::Write(const WriteOptions& write_options, WriteBatch* my_batch) {  
  if (my_batch == nullptr) {  
    return Status::Corruption("Batch is nullptr!");  
  }  
  PERF_TIMER_GUARD(write_pre_and_post_process_time);  
  // WriteThread::Writer是一个写任务的抽象结构，代表了用户的一次写操作。其中的batch字段存有  
  // 实际需要写入的数据，sync字段指明这个写操作需不需要对事务日志执行fsync/fdatasync操作，而  
  // disableWAL指明是否需要写事务日志，done字段在该写操作完成时设置，timeout_hint_us指明了  
  // 这个写操作完成时间期限。  
  // 最后，in_batch_group的比较有意思。在RocksDB内部，对写入操作做了优化，尽可能地将用户的写入  
  // 批量处理。这其中使用了一个队列，即write_thread_内部的WriteThread::Writer*队列。在准备写队列头  
  // 的任务时，会试着用BuildBatchGroup()构建一个批量任务组，将紧跟着队头的其他写操作任务加入  
  // 到一个BatchGroup，一次性地写入数据库。  
  WriteThread::Writer w(&mutex_);  
  w.batch = my_batch;  
  w.sync = write_options.sync;  
  w.disableWAL = write_options.disableWAL;  
  w.in_batch_group = false;  
  w.done = false;  
  w.timeout_hint_us = write_options.timeout_hint_us;  
  
  uint64_t expiration_time = 0;  
  bool has_timeout = false;  
  if (w.timeout_hint_us == 0) {  
    w.timeout_hint_us = WriteThread::kNoTimeOut;  
  } else {  
    expiration_time = env_->NowMicros() + w.timeout_hint_us;  
    has_timeout = true;  
  }  
  
  if (!write_options.disableWAL) {  
    RecordTick(stats_, WRITE_WITH_WAL);  
  }  
  
  // ???  
  WriteContext context;  
  mutex_.Lock();  
  
  if (!write_options.disableWAL) {  
    default_cf_internal_stats_->AddDBStats(InternalStats::WRITE_WITH_WAL, 1);  
  }  
  
  // 将当前写入任务@w挂入写队列，并在mutex_上睡眠等待。等待直到:  
  // 1) 写操作设置了超时时间，等待超时。或，  
  // 2) @w之前的任务都已完成，@w已处于队列头部。或，  
  // 3) @w这个写任务被别的写线程完成了。  
  // 第3个条件，任务被别的写线程完成，实际上是被之前的写任务合并进一个  
  // WriteBatchGroup中去了。此时的@w会被标记成in_batch_group。有意思的是，在EnterWriteThread()  
  // 里面，如果因为超时唤醒了，发现当前任务in_batch_group为true，则会继续等待，  
  // 因为它已经被别的线程加入BatchGroup准备写入数据库了。  
  Status status = write_thread_.EnterWriteThread(&w, expiration_time);  
  assert(status.ok() || status.IsTimedOut());  
  if (status.IsTimedOut()) {  
    mutex_.Unlock();  
    RecordTick(stats_, WRITE_TIMEDOUT);  
    return Status::TimedOut();  
  }  
  if (w.done) {  // write was done by someone else  
    default_cf_internal_stats_->AddDBStats(InternalStats::WRITE_DONE_BY_OTHER,  
                                           1);  
    mutex_.Unlock();  
    RecordTick(stats_, WRITE_DONE_BY_OTHER);  
    return w.status;  
  }  
  
  RecordTick(stats_, WRITE_DONE_BY_SELF);  
  default_cf_internal_stats_->AddDBStats(InternalStats::WRITE_DONE_BY_SELF, 1);  
  
  // Once reaches this point, the current writer "w" will try to do its write  
  // job.  It may also pick up some of the remaining writers in the "writers_"  
  // when it finds suitable, and finish them in the same write batch.  
  // This is how a write job could be done by the other writer.  
  assert(!single_column_family_mode_ ||  
         versions_->GetColumnFamilySet()->NumberOfColumnFamilies() == 1);  
  
  uint64_t max_total_wal_size = (db_options_.max_total_wal_size == 0)  
                                    ? 4 * max_total_in_memory_state_  
                                    : db_options_.max_total_wal_size;  
  if (UNLIKELY(!single_column_family_mode_) &&  
      alive_log_files_.begin()->getting_flushed == false &&  
      total_log_size_ > max_total_wal_size) {  
    // 如果column family有多个，最早的活跃的事务日志对应的memtable还没有被写入磁盘，  
    // 而且当前日志总大小超过了设定的最大值，那么就需要分配新的memtable，将老的  
    // immutable memtable内容写入磁盘。  
    uint64_t flush_column_family_if_log_file = alive_log_files_.begin()->number;  
    alive_log_files_.begin()->getting_flushed = true;  
    Log(InfoLogLevel::INFO_LEVEL, db_options_.info_log,  
        "Flushing all column families with data in WAL number %" PRIu64  
        ". Total log size is %" PRIu64 " while max_total_wal_size is %" PRIu64,  
        flush_column_family_if_log_file, total_log_size_, max_total_wal_size);  
    // no need to refcount because drop is happening in write thread, so can't  
    // happen while we're in the write thread  
    for (auto cfd : *versions_->GetColumnFamilySet()) {  
      if (cfd->IsDropped()) {  
        continue;  
      }  
      if (cfd->GetLogNumber() <= flush_column_family_if_log_file) {  
        status = SetNewMemtableAndNewLogFile(cfd, &context);  
        if (!status.ok()) {  
          break;  
        }  
        cfd->imm()->FlushRequested();  
        SchedulePendingFlush(cfd);  
        context.schedule_bg_work_ = true;  
      }  
    }  
  } else if (UNLIKELY(write_buffer_.ShouldFlush())) {  
    Log(InfoLogLevel::INFO_LEVEL, db_options_.info_log,  
        "Flushing all column families. Write buffer is using %" PRIu64  
        " bytes out of a total of %" PRIu64 ".",  
        write_buffer_.memory_usage(), write_buffer_.buffer_size());  
    // no need to refcount because drop is happening in write thread, so can't  
    // happen while we're in the write thread  
    for (auto cfd : *versions_->GetColumnFamilySet()) {  
      if (cfd->IsDropped()) {  
        continue;  
      }  
      if (!cfd->mem()->IsEmpty()) {  
        status = SetNewMemtableAndNewLogFile(cfd, &context);  
        if (!status.ok()) {  
          break;  
        }  
        cfd->imm()->FlushRequested();  
        SchedulePendingFlush(cfd);  
        context.schedule_bg_work_ = true;  
      }  
    }  
    MaybeScheduleFlushOrCompaction();  
  }  
  
  if (UNLIKELY(status.ok() && !bg_error_.ok())) {  
    status = bg_error_;  
  }  
  
  if (UNLIKELY(status.ok() && !flush_scheduler_.Empty())) {  
    status = ScheduleFlushes(&context);  
  }  
  
  if (UNLIKELY(status.ok() && (write_controller_.IsStopped() ||  
                               write_controller_.GetDelay() > 0))) {  
    // If writer is stopped, we need to get it going,  
    // so schedule flushes/compactions  
    if (context.schedule_bg_work_) {  
      MaybeScheduleFlushOrCompaction();  
    }  
    status = DelayWrite(expiration_time);  
  }  
  
  if (UNLIKELY(status.ok() && has_timeout &&  
               env_->NowMicros() > expiration_time)) {  
    status = Status::TimedOut();  
  }  
  
  uint64_t last_sequence = versions_->LastSequence();  
  WriteThread::Writer* last_writer = &w;  
  if (status.ok()) {  
    autovector<WriteBatch*> write_batch_group;  
    write_thread_.BuildBatchGroup(&last_writer, &write_batch_group);  
  
    // Add to log and apply to memtable.  We can release the lock  
    // during this phase since &w is currently responsible for logging  
    // and protects against concurrent loggers and concurrent writes  
    // into memtables  
    {  
      mutex_.Unlock();  
      WriteBatch* updates = nullptr;  
      if (write_batch_group.size() == 1) {  
        updates = write_batch_group[0];  
      } else {  
        updates = &tmp_batch_;  
        for (size_t i = 0; i < write_batch_group.size(); ++i) {  
          WriteBatchInternal::Append(updates, write_batch_group[i]);  
        }  
      }  
  
      const SequenceNumber current_sequence = last_sequence + 1;  
      WriteBatchInternal::SetSequence(updates, current_sequence);  
      int my_batch_count = WriteBatchInternal::Count(updates);  
      last_sequence += my_batch_count;  
      const uint64_t batch_size = WriteBatchInternal::ByteSize(updates);  
      // Record statistics  
      RecordTick(stats_, NUMBER_KEYS_WRITTEN, my_batch_count);  
      RecordTick(stats_, BYTES_WRITTEN, batch_size);  
      if (write_options.disableWAL) {  
        flush_on_destroy_ = true;  
      }  
      PERF_TIMER_STOP(write_pre_and_post_process_time);  
  
      uint64_t log_size = 0;  
      if (!write_options.disableWAL) {  
        PERF_TIMER_GUARD(write_wal_time);  
        Slice log_entry = WriteBatchInternal::Contents(updates);  
        status = log_->AddRecord(log_entry);  
        total_log_size_ += log_entry.size();  
        alive_log_files_.back().AddSize(log_entry.size());  
        log_empty_ = false;  
        log_size = log_entry.size();  
        RecordTick(stats_, WAL_FILE_BYTES, log_size);  
        if (status.ok() && write_options.sync) {  
          RecordTick(stats_, WAL_FILE_SYNCED);  
          StopWatch sw(env_, stats_, WAL_FILE_SYNC_MICROS);  
          if (db_options_.use_fsync) {  
            status = log_->file()->Fsync();  
          } else {  
            status = log_->file()->Sync();  
          }  
          if (status.ok() && !log_dir_synced_) {  
            // We only sync WAL directory the first time WAL syncing is  
            // requested, so that in case users never turn on WAL sync,  
            // we can avoid the disk I/O in the write code path.  
            status = directories_.GetWalDir()->Fsync();  
          }  
          log_dir_synced_ = true;  
        }  
      }  
      if (status.ok()) {  
        PERF_TIMER_GUARD(write_memtable_time);  
  
        status = WriteBatchInternal::InsertInto(  
            updates, column_family_memtables_.get(),  
            write_options.ignore_missing_column_families, 0, this, false);  
        // A non-OK status here indicates iteration failure (either in-memory  
        // writebatch corruption (very bad), or the client specified invalid  
        // column family).  This will later on trigger bg_error_.  
        //  
        // Note that existing logic was not sound. Any partial failure writing  
        // into the memtable would result in a state that some write ops might  
        // have succeeded in memtable but Status reports error for all writes.  
  
        SetTickerCount(stats_, SEQUENCE_NUMBER, last_sequence);  
      }  
      PERF_TIMER_START(write_pre_and_post_process_time);  
      if (updates == &tmp_batch_) {  
        tmp_batch_.Clear();  
      }  
      mutex_.Lock();  
      // internal stats  
      default_cf_internal_stats_->AddDBStats(  
          InternalStats::BYTES_WRITTEN, batch_size);  
      default_cf_internal_stats_->AddDBStats(InternalStats::NUMBER_KEYS_WRITTEN,  
                                             my_batch_count);  
      if (!write_options.disableWAL) {  
        default_cf_internal_stats_->AddDBStats(  
            InternalStats::WAL_FILE_SYNCED, 1);  
        default_cf_internal_stats_->AddDBStats(  
            InternalStats::WAL_FILE_BYTES, log_size);  
      }  
      if (status.ok()) {  
        versions_->SetLastSequence(last_sequence);  
      }  
    }  
  }  
  if (db_options_.paranoid_checks && !status.ok() &&  
      !status.IsTimedOut() && bg_error_.ok()) {  
    bg_error_ = status; // stop compaction & fail any further writes  
  }  
  
  write_thread_.ExitWriteThread(&w, last_writer, status);  
  
  if (context.schedule_bg_work_) {  
    MaybeScheduleFlushOrCompaction();  
  }  
  mutex_.Unlock();  
  
  if (status.IsTimedOut()) {  
    RecordTick(stats_, WRITE_TIMEDOUT);  
  }  
  
  return status;  
}  
