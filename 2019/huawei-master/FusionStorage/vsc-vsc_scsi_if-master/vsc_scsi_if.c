/********************************************************************
            Copyright (C) Huawei Technologies, 2015
  #作者：Peng Ruilin (pengruilin@huawei.com)
  #描述: virtual storage controller驱动scsi接口模块
         用于支持vsc驱动的不复位OS的升级功能。
********************************************************************/
#include "vsc_scsi_if.h"

#define VSC_SCSI_IF_PROC_CTL_FILE  "vsc_scsi_if"

/* scsi接口函数指针 */
static struct vsc_scsi_host_operation *g_scsi_hook_op = NULL;

/* 是否停止驱动 */
static int g_scsi_hook_if_stop = 0;

/* /proc/vsc目录指针 */
struct proc_dir_entry *proc_vsc_root = NULL;
EXPORT_SYMBOL(proc_vsc_root);


/* scsi host结构体指针 */
static struct list_head              scsi_if_vss_list;
static DEFINE_MUTEX(scsi_if_vss_list_lock);

struct vsc_scsi_struct {
    struct list_head     list;                 /* scsi host链表头 */
    struct Scsi_Host     *sh;                  /* scsh host指针 */
    void                 *private_data;        /* 私有数据，指向vsc模块中的vsc_ctlr_info结构 */
    void                 *data;                /* 在vsc离线时存储的临时数据 */
};

static atomic_t             vsc_users;             /* vsc引用计数 */
static struct completion    *vsc_unload_complete;  /* 驱动卸载等待 */
static spinlock_t           vsc_unload_lock;       

#ifdef DRIVER_VER
static char banner[] __initdata = KERN_INFO "Huawei Cloudstorage virtual storage controller scsi interface driver "DRIVER_VER" initialized.\n";
#else
static char banner[] __initdata = KERN_INFO "Huawei Cloudstorage virtual storage controller scsi interface driver initialized.\n";
#endif

static void *g_vsc_mem_pool = NULL;
/*需要判断IS_ERR(retval)*/
void *vsc_scsi_if_alloc_pool(int size)
{
    if (g_vsc_mem_pool) {
        return ERR_PTR(-EEXIST);
    }
    g_vsc_mem_pool = kzalloc(size, GFP_KERNEL);

    return g_vsc_mem_pool;
}
EXPORT_SYMBOL(vsc_scsi_if_alloc_pool);

void vsc_scsi_if_free_pool(void)
{
    if (g_vsc_mem_pool) {
        kfree(g_vsc_mem_pool);
        g_vsc_mem_pool = NULL;
    }
}
EXPORT_SYMBOL(vsc_scsi_if_free_pool);

void *vsc_scsi_if_get_pool(void)
{
    return g_vsc_mem_pool;
}
EXPORT_SYMBOL(vsc_scsi_if_get_pool);

/**************************************************************************
 功能描述  : vsc驱动是否处于停止状态。
 参    数  : 无
 返 回 值  : 无
**************************************************************************/
static inline int vsc_scsi_if_should_stop(void)
{
    return unlikely(g_scsi_hook_if_stop == 1);
}

/**************************************************************************
 功能描述  : vsc代码引用计数+1
 参    数  : 无
 返 回 值  : 无
**************************************************************************/
inline void vsc_scsi_if_scmnd_inc(void)
{
    atomic_inc(&vsc_users);    
}

/**************************************************************************
 功能描述  : vsc代码引用计数-1
 参    数  : 无
 返 回 值  : 无 
**************************************************************************/
inline void vsc_scsi_if_scmnd_dec(void)
{
    if (atomic_dec_and_test(&vsc_users)) {
        /* 当为0时，若有等待任务，则进行唤醒 */
        unsigned long flags;
        spin_lock_irqsave(&vsc_unload_lock, flags);
        if (vsc_unload_complete) {
            complete(vsc_unload_complete); 
        }
        spin_unlock_irqrestore(&vsc_unload_lock, flags);
    }
}

/**************************************************************************
 功能描述  : 等待vsc代码执行完毕
 参    数  : 无
 返 回 值  : 无
**************************************************************************/
inline void vsc_scsi_if_wait_scmnd_complete(void)
{
    if (atomic_read(&vsc_users) > 0 ) {
        unsigned long flags;
        DECLARE_COMPLETION_ONSTACK(c);

        spin_lock_irqsave(&vsc_unload_lock, flags);
        vsc_unload_complete = &c;
        spin_unlock_irqrestore(&vsc_unload_lock, flags);

        wait_for_completion(vsc_unload_complete);
        vsc_unload_complete = NULL;
    }
}

/**************************************************************************
 功能描述  : 注册的接口函数是否有效
 参    数  : 无
 返 回 值  : 无
**************************************************************************/
static inline int vsc_valid_sht(void)
{
    if (likely(g_scsi_hook_op && g_scsi_hook_op->sht)) {
        return 1;
    }

    return 0;
}

static inline int vsc_valid_stt(void)
{
    if (likely(g_scsi_hook_op && g_scsi_hook_op->stt)) {
        return 1;
    }

    return 0;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static const char * vsc_scsi_if_info(struct Scsi_Host *sh)
{
    const char *ret = NULL;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = NULL;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = NULL;
        goto out;
    }

    if (!g_scsi_hook_op->sht->info) {
        ret = NULL;
        goto out;
    }

    ret = g_scsi_hook_op->sht->info(sh);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static int vsc_scsi_if_ioctl(struct scsi_device *sdev, int cmd, void __user *arg)
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = -EINVAL;  //-EBUSY;热补丁卸载后函数的返回值跟该函数为NULL的返回值一样
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = -EINVAL;  //-EFAULT;
        goto out;
    }

    if (!g_scsi_hook_op->sht->ioctl) {
        ret = -EINVAL; //-EFAULT;
        goto out;
    }

    ret = g_scsi_hook_op->sht->ioctl(sdev, cmd, arg);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
#ifdef CONFIG_COMPAT
static int vsc_scsi_if_compat_ioctl(struct scsi_device *sdev, int cmd, void __user *arg)
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = -ENOIOCTLCMD; //-EBUSY;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = -ENOIOCTLCMD; //-EFAULT;
        goto out;
    }

    if (!g_scsi_hook_op->sht->compat_ioctl) {
        ret = -ENOIOCTLCMD; //-EFAULT;
        goto out;
    }

    ret = g_scsi_hook_op->sht->compat_ioctl(sdev, cmd, arg);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}
#endif


/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
#ifdef DEF_SCSI_QCMD
static int vsc_scsi_if_queuecommand(struct Scsi_Host *shost, struct scsi_cmnd *cmd)
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = SCSI_MLQUEUE_HOST_BUSY;
        goto out;
    }  

    if (!vsc_valid_sht()) {
        ret = SCSI_MLQUEUE_HOST_BUSY;
        goto out;
    }
    ret = g_scsi_hook_op->sht->queuecommand(shost, cmd);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}
#else
static int vsc_scsi_if_queuecommand(struct scsi_cmnd *sc, void (*done)(struct scsi_cmnd *)) 
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret =  SCSI_MLQUEUE_HOST_BUSY;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = SCSI_MLQUEUE_HOST_BUSY;
        goto out;
    }

    ret =  g_scsi_hook_op->sht->queuecommand(sc, done);
out:
    vsc_scsi_if_scmnd_dec();

    return ret;
}
#endif

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
#if LINUX_VERSION_CODE > KERNEL_VERSION(2, 6, 21)   

static int vsc_scsi_if_transfer_response(struct scsi_cmnd *sc, void (*done)(struct scsi_cmnd *))
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = SCSI_MLQUEUE_HOST_BUSY;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = SCSI_MLQUEUE_HOST_BUSY;
        goto out;
    }

    if (!g_scsi_hook_op->sht->transfer_response) {
        ret = SCSI_MLQUEUE_HOST_BUSY;
        goto out;
    }

    ret = g_scsi_hook_op->sht->transfer_response(sc, done);

out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

#endif
/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static int vsc_scsi_if_eh_abort_handler(struct scsi_cmnd *sc)
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = SUCCESS;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = FAILED;
        goto out;
    }

    if (!g_scsi_hook_op->sht->eh_abort_handler) {
        ret = FAILED;
        goto out;
    }

    ret = g_scsi_hook_op->sht->eh_abort_handler(sc);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static int vsc_scsi_if_eh_device_reset_handler(struct scsi_cmnd *sc)
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = SUCCESS;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = FAILED;
        goto out;
    }

    if (!g_scsi_hook_op->sht->eh_device_reset_handler) {
        ret = FAILED;
        goto out;
    }

    ret = g_scsi_hook_op->sht->eh_device_reset_handler(sc);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
#if LINUX_VERSION_CODE > KERNEL_VERSION(2, 6, 25)  

static int vsc_scsi_if_eh_target_reset_handler(struct scsi_cmnd *sc)
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = SUCCESS;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = FAILED;
        goto out;
    }

    if (!g_scsi_hook_op->sht->eh_target_reset_handler) {
        ret = FAILED;
        goto out;
    }

    ret = g_scsi_hook_op->sht->eh_target_reset_handler(sc);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

#endif
/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static int vsc_scsi_if_eh_bus_reset_handler(struct scsi_cmnd *sc)
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = SUCCESS;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = FAILED;
        goto out;
    }

    if (!g_scsi_hook_op->sht->eh_bus_reset_handler) {
        ret = FAILED;
        goto out;
    }

    ret = g_scsi_hook_op->sht->eh_bus_reset_handler(sc);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static int vsc_scsi_if_eh_host_reset_handler(struct scsi_cmnd *sc)
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = SUCCESS;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = FAILED;
        goto out;
    }

    if (!g_scsi_hook_op->sht->eh_host_reset_handler) {
        ret = FAILED;
        goto out;
    }

    ret = g_scsi_hook_op->sht->eh_host_reset_handler(sc);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static int vsc_scsi_if_slave_alloc(struct scsi_device *sdev)
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = 0;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = 0;
        goto out;
    }

    if (!g_scsi_hook_op->sht->slave_alloc) {
        ret = 0;
        goto out;
    }

    ret = g_scsi_hook_op->sht->slave_alloc(sdev);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static int vsc_scsi_if_slave_configure(struct scsi_device *sdev)
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = 0;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = 0;
        goto out;
    }

    if (!g_scsi_hook_op->sht->slave_configure) {
        ret = 0;
        goto out;
    }

    ret = g_scsi_hook_op->sht->slave_configure(sdev);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static void vsc_scsi_if_slave_destroy(struct scsi_device *sdev)
{
    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        goto out;
    }

    if (!vsc_valid_sht()) {
        goto out;
    }

    if (!g_scsi_hook_op->sht->slave_destroy) {
        goto out;
    }

    g_scsi_hook_op->sht->slave_destroy(sdev);
out:
    vsc_scsi_if_scmnd_dec();
    return ;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static int vsc_scsi_if_target_alloc(struct scsi_target *starget)
{
    int ret = 0; 
    vsc_scsi_if_scmnd_inc();

    if (vsc_scsi_if_should_stop()) {
        ret = 0;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = 0;
        goto out;
    }

    if (!g_scsi_hook_op->sht->target_alloc) {
        ret = 0;
        goto out;
    }

    ret = g_scsi_hook_op->sht->target_alloc(starget);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static void vsc_scsi_if_target_destroy(struct scsi_target *starget)
{
    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        goto out;
    }

    if (!vsc_valid_sht()) {
        goto out;
    }

    if (!g_scsi_hook_op->sht->target_destroy) {
        goto out;
    }

    g_scsi_hook_op->sht->target_destroy(starget);
out:
    vsc_scsi_if_scmnd_dec(); 
    return ;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static int vsc_scsi_if_scan_finished(struct Scsi_Host *shost, unsigned long time)
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();

    if (vsc_scsi_if_should_stop()) {
        ret = 1;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = 1;
        goto out;
    }

    if (!g_scsi_hook_op->sht->scan_finished) {
        ret = 1;
        goto out;
    }

    ret = g_scsi_hook_op->sht->scan_finished(shost, time);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static void vsc_scsi_if_scan_start(struct Scsi_Host *sh)
{
    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        goto out;
    }

    if (!vsc_valid_sht()) {
        goto out;
    }

    if (!g_scsi_hook_op->sht->scan_start) {
        goto out;
    }

    g_scsi_hook_op->sht->scan_start(sh);
out:
    vsc_scsi_if_scmnd_dec();
    return ;
}


/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
#if LINUX_VERSION_CODE >= KERNEL_VERSION(2, 6, 35)
static void vsc_scsi_if_unlock_native_capacity(struct scsi_device *sdev)
{
    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        goto out;
    }

    if (!vsc_valid_sht()) {
        goto out;
    }

    if (!g_scsi_hook_op->sht->unlock_native_capacity) {
        goto out;
    }

    g_scsi_hook_op->sht->unlock_native_capacity(sdev);
out:
    vsc_scsi_if_scmnd_dec();
    return ;
}
#endif

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
#if (LINUX_VERSION_CODE < KERNEL_VERSION(2, 6, 32))
static int vsc_scsi_if_change_queue_depth(struct scsi_device *sdev, int qdepth)
#else
static int vsc_scsi_if_change_queue_depth(struct scsi_device *sdev, int qdepth, int reason)
#endif
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = -EBUSY;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = -EOPNOTSUPP;
        goto out;
    }

    if (!g_scsi_hook_op->sht->change_queue_depth) {
        ret = -EOPNOTSUPP;
        goto out;
    }
#if (LINUX_VERSION_CODE < KERNEL_VERSION(2, 6, 32))
	ret = g_scsi_hook_op->sht->change_queue_depth(sdev, qdepth);
#else
    ret = g_scsi_hook_op->sht->change_queue_depth(sdev, qdepth, reason);
#endif
	
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static int vsc_scsi_if_change_queue_type(struct scsi_device *sdev, int tag_type)
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = -EBUSY;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = -EOPNOTSUPP;
        goto out;
    }

    if (!g_scsi_hook_op->sht->change_queue_type) {
        ret = -EOPNOTSUPP;
        goto out;
    }

    ret = g_scsi_hook_op->sht->change_queue_type(sdev, tag_type);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
static int vsc_scsi_if_bios_param(struct scsi_device *sdev, struct block_device *bdev, sector_t capacity, int geom[])
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = -EBUSY;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = -EFAULT;
        goto out;
    }

    if (!g_scsi_hook_op->sht->bios_param) {
        ret = -EFAULT;
        goto out;
    }

    ret = g_scsi_hook_op->sht->bios_param(sdev, bdev, capacity, geom);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
#if LINUX_VERSION_CODE < KERNEL_VERSION(3, 10, 0)
static int vsc_scsi_if_proc_info(struct Scsi_Host *sh, char *buf, char **start, off_t off, int len, int in)
{
    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = -EBUSY;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = -EFAULT;
        goto out;
    }

    if (!g_scsi_hook_op->sht->proc_info) {
        ret = -EFAULT;
        goto out;
    }

    ret = g_scsi_hook_op->sht->proc_info(sh, buf, start, off, len, in);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}
#else
static int vsc_scsi_if_show_info(struct seq_file *file, struct Scsi_Host *shost)
{

    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = -EBUSY;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = -EFAULT;
        goto out;
    }

    if (!g_scsi_hook_op->sht->show_info) {
        ret = -EFAULT;
        goto out;
    }

    ret = g_scsi_hook_op->sht->show_info(file, shost);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

static int vsc_scsi_if_write_info(struct Scsi_Host *shost, char *string, int len)
{

    int ret = 0;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = -EBUSY;
        goto out;
    }

    if (!vsc_valid_sht()) {
        ret = -EFAULT;
        goto out;
    }

    if (!g_scsi_hook_op->sht->write_info) {
        ret = -EFAULT;
        goto out;
    }

    ret = g_scsi_hook_op->sht->write_info(shost, string, len);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}
#endif

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
#if LINUX_VERSION_CODE > KERNEL_VERSION(2, 6, 26)
static enum blk_eh_timer_return vsc_scsi_if_eh_timed_out(struct scsi_cmnd *sc)
{
    enum blk_eh_timer_return ret = BLK_EH_NOT_HANDLED;
#else
static enum scsi_eh_timer_return vsc_scsi_if_eh_timed_out(struct scsi_cmnd *sc)
{
	enum scsi_eh_timer_return ret = EH_NOT_HANDLED;
#endif
    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        goto out;
    }

    if (!vsc_valid_sht()) {
        goto out;
    }

    if (!g_scsi_hook_op->sht->eh_timed_out) {
        goto out;
    }

    ret = g_scsi_hook_op->sht->eh_timed_out(sc);;
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**
 *    注册给scsi中层的驱动模板
 **/
static struct scsi_host_template vsc_scsi_driver_template = {
    .module               = THIS_MODULE,
    .name                 = "vsc",
    .proc_name            = "vsc",
    .this_id              = -1,
    .can_queue            = 1,
    .sg_tablesize         = 128,
    .max_sectors          = 8192,
    .use_clustering       = ENABLE_CLUSTERING,
    /* 函数列表 */
    .info                    = NULL,
    .ioctl                   = NULL,
#ifdef CONFIG_COMPAT
    .compat_ioctl            = NULL,
#endif
    .queuecommand            = vsc_scsi_if_queuecommand,
#if LINUX_VERSION_CODE > KERNEL_VERSION(2, 6, 21)   
    .transfer_response       = vsc_scsi_if_transfer_response,
#endif
    .eh_abort_handler        = vsc_scsi_if_eh_abort_handler, 
    .eh_device_reset_handler = NULL,
#if LINUX_VERSION_CODE > KERNEL_VERSION(2, 6, 25)    
    .eh_target_reset_handler = NULL,
#endif
    .eh_bus_reset_handler    = NULL,
    .eh_host_reset_handler   = NULL,
    .slave_alloc             = NULL,
    .slave_configure         = NULL,
    .slave_destroy           = NULL,
    .target_alloc            = NULL,
    .target_destroy          = NULL,
    .scan_finished           = NULL,
    .scan_start              = NULL,
    .change_queue_depth      = NULL,
    .change_queue_type       = NULL,
    .bios_param              = NULL,
#if LINUX_VERSION_CODE < KERNEL_VERSION(3, 10, 0)
    .proc_info               = vsc_scsi_if_proc_info,
#else
    .show_info               = vsc_scsi_if_show_info,
    .write_info              = vsc_scsi_if_write_info,
#endif
    .eh_timed_out            = NULL,
};

/**************************************************************************
 功能描述  : 初始化scsi host驱动模板
 参    数  : 无
 返 回 值  : 
**************************************************************************/
void vsc_scsi_if_setup_host_template(struct scsi_host_template *sht) 
{
    /* 初始化结构数据 */
    vsc_scsi_driver_template.can_queue  = sht->can_queue;
    vsc_scsi_driver_template.sg_tablesize = sht->sg_tablesize;
    vsc_scsi_driver_template.max_sectors = sht->max_sectors;
    vsc_scsi_driver_template.dma_boundary = sht->dma_boundary;
    vsc_scsi_driver_template.cmd_per_lun = sht->cmd_per_lun;
#if LINUX_VERSION_CODE > KERNEL_VERSION(2, 6, 23)       
    vsc_scsi_driver_template.supported_mode = sht->supported_mode;
#endif
    vsc_scsi_driver_template.use_clustering = sht->use_clustering;
    vsc_scsi_driver_template.emulated = sht->emulated;
    vsc_scsi_driver_template.skip_settle_delay = sht->skip_settle_delay;
    vsc_scsi_driver_template.ordered_tag = sht->ordered_tag;

    /* 需要设置为NULL的自定函数 */

    vsc_scsi_driver_template.info                       = (sht->info) ? vsc_scsi_if_info : NULL;
    vsc_scsi_driver_template.ioctl                      = (sht->ioctl) ? vsc_scsi_if_ioctl : NULL;
#ifdef CONFIG_COMPAT
    vsc_scsi_driver_template.compat_ioctl               = (sht->compat_ioctl) ? vsc_scsi_if_compat_ioctl : NULL;
#endif
    vsc_scsi_driver_template.eh_device_reset_handler    = (sht->eh_device_reset_handler) ? vsc_scsi_if_eh_device_reset_handler : NULL;
#if LINUX_VERSION_CODE > KERNEL_VERSION(2, 6, 25)   
    vsc_scsi_driver_template.eh_target_reset_handler    = (sht->eh_target_reset_handler) ? vsc_scsi_if_eh_target_reset_handler : NULL;
#endif
    vsc_scsi_driver_template.eh_bus_reset_handler       = (sht->eh_bus_reset_handler) ? vsc_scsi_if_eh_bus_reset_handler : NULL;
    vsc_scsi_driver_template.eh_host_reset_handler      = (sht->eh_host_reset_handler) ? vsc_scsi_if_eh_host_reset_handler : NULL;
    vsc_scsi_driver_template.slave_alloc                = (sht->slave_alloc) ? vsc_scsi_if_slave_alloc : NULL;
    vsc_scsi_driver_template.slave_configure            = (sht->slave_configure) ? vsc_scsi_if_slave_configure : NULL;
    vsc_scsi_driver_template.slave_destroy              = (sht->slave_destroy) ? vsc_scsi_if_slave_destroy : NULL;
    vsc_scsi_driver_template.target_alloc               = (sht->target_alloc) ? vsc_scsi_if_target_alloc : NULL;
    vsc_scsi_driver_template.target_destroy             = (sht->target_destroy) ? vsc_scsi_if_target_destroy : NULL;
    vsc_scsi_driver_template.bios_param                 = (sht->bios_param) ? vsc_scsi_if_bios_param : NULL;
    vsc_scsi_driver_template.change_queue_depth         = (sht->change_queue_depth) ? vsc_scsi_if_change_queue_depth : NULL;
    vsc_scsi_driver_template.change_queue_type          = (sht->change_queue_type) ? vsc_scsi_if_change_queue_type : NULL;
    vsc_scsi_driver_template.scan_start                 = (sht->scan_start) ? vsc_scsi_if_scan_start : NULL;
    vsc_scsi_driver_template.scan_finished              = (sht->scan_finished) ? vsc_scsi_if_scan_finished : NULL;
#if LINUX_VERSION_CODE >= KERNEL_VERSION(2, 6, 35)
    vsc_scsi_driver_template.unlock_native_capacity     = (sht->unlock_native_capacity) ? vsc_scsi_if_unlock_native_capacity : NULL;
#endif
    vsc_scsi_driver_template.eh_timed_out               = (sht->eh_timed_out) ? vsc_scsi_if_eh_timed_out : NULL;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
int vsc_scsi_if_user_scan(struct Scsi_Host *sh, uint channel, uint id, uint lun)
{
    int ret = -EINVAL;//-ENXIO;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = -EINVAL;//-ENXIO;
        goto out;
    }

    if (!vsc_valid_stt()) {
        ret = -EINVAL;//-ENXIO;
        goto out;
    }

    if (!g_scsi_hook_op->stt->user_scan) {
        ret = -EINVAL;//-ENXIO;
        goto out;
    }

    ret = g_scsi_hook_op->stt->user_scan(sh, channel, id, lun);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
void vsc_scsi_if_eh_strategy_handler(struct Scsi_Host *sh)
{
    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        goto out;
    }

    if (!vsc_valid_stt()) {
        goto out;
    }

    if (!g_scsi_hook_op->stt->eh_strategy_handler) {
        goto out;
    }

    g_scsi_hook_op->stt->eh_strategy_handler(sh);
out:
    vsc_scsi_if_scmnd_dec();
    return ;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
#if LINUX_VERSION_CODE > KERNEL_VERSION(2, 6, 26)   
static enum blk_eh_timer_return vsc_scsi_if_stt_eh_timed_out(struct scsi_cmnd *sc)
{
    enum blk_eh_timer_return ret = BLK_EH_NOT_HANDLED;
#else
static enum scsi_eh_timer_return vsc_scsi_if_stt_eh_timed_out(struct scsi_cmnd *sc)
{
	enum scsi_eh_timer_return ret = EH_NOT_HANDLED;	
#endif

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        goto out;
    }

    if (!vsc_valid_stt()) {
        goto out;
    }

    if (!g_scsi_hook_op->stt->eh_timed_out) {
        goto out;
    }

    ret = g_scsi_hook_op->stt->eh_timed_out(sc);;
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}

/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
#if LINUX_VERSION_CODE > KERNEL_VERSION(2, 6, 23) 
int vsc_scsi_if_it_nexus_response(struct Scsi_Host *sh, u64 itn_id, int result)
{
    int ret = -EINVAL;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = -EINVAL; //-EBUSY;
        goto out;
    }

    if (!vsc_valid_stt()) {
        ret = -EINVAL;
        goto out;
    }

    if (!g_scsi_hook_op->stt->it_nexus_response) {
        ret = -EINVAL;
        goto out;
    }

    ret = g_scsi_hook_op->stt->it_nexus_response(sh, itn_id, result);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}


/**************************************************************************
 功能描述  : scsi中层接口函数
 参    数  : 无
 返 回 值  : 
**************************************************************************/
int vsc_scsi_if_tsk_mgmt_response(struct Scsi_Host *sh, u64 itn_id, u64 mid, int result)
{
    int ret = -EINVAL;

    vsc_scsi_if_scmnd_inc();
    if (vsc_scsi_if_should_stop()) {
        ret = -EINVAL;//-EBUSY;
        goto out;
    }

    if (!vsc_valid_stt()) {
        ret = -EINVAL;
        goto out;
    }

    if (!g_scsi_hook_op->stt->tsk_mgmt_response) {
        ret = -EINVAL;
        goto out;
    }

    ret = g_scsi_hook_op->stt->tsk_mgmt_response(sh, itn_id, mid, result);
out:
    vsc_scsi_if_scmnd_dec();
    return ret;
}
#endif
/* 注册给中层的scsi_transport_template模板 */
static struct scsi_transport_template vsc_scsi_transport_template = {
    .user_scan               = NULL,
    .eh_strategy_handler     = NULL,
    .eh_timed_out            = NULL,
#if LINUX_VERSION_CODE > KERNEL_VERSION(2, 6, 23)    
    .it_nexus_response       = vsc_scsi_if_it_nexus_response,
    .tsk_mgmt_response       = vsc_scsi_if_tsk_mgmt_response,
#endif
};

/**************************************************************************
 功能描述  : 初始化transportt驱动模板
 参    数  : 无
 返 回 值  : 
**************************************************************************/
void vsc_scsi_if_setup_transport_template(struct scsi_transport_template *stt)
{
    if (!stt) {
        return;
    }

    vsc_scsi_transport_template.device_size = stt->device_size;
    vsc_scsi_transport_template.target_size = stt->target_size;
    vsc_scsi_transport_template.host_size = stt->host_size;
    vsc_scsi_transport_template.create_work_queue = stt->create_work_queue;


    /* 需要设置为NULL的自定函数 */
    vsc_scsi_transport_template.user_scan           = (stt->user_scan) ? vsc_scsi_if_user_scan : NULL;
    vsc_scsi_transport_template.eh_strategy_handler = (stt->eh_strategy_handler) ? vsc_scsi_if_eh_strategy_handler : NULL;
    vsc_scsi_transport_template.eh_timed_out        = (stt->eh_timed_out) ? vsc_scsi_if_stt_eh_timed_out : NULL;
}

/**************************************************************************
 功能描述  : 封装的Scsi_Host结构体申请函数
 参    数  : 无
 返 回 值  : scsi控制句柄
**************************************************************************/
struct vsc_scsi_struct *vsc_scsi_if_alloc(void)
{
    struct vsc_scsi_struct *vss = NULL;
    struct Scsi_Host *sh = NULL;
    int ret = 0;

    if (vsc_scsi_if_should_stop()) {
        return NULL;
    }

    sh = scsi_host_alloc(&vsc_scsi_driver_template, sizeof(struct vsc_scsi_struct));
    if (!sh) {
        printk("register scsi driver template failed, not enough memory.\n");
        ret = -ENOMEM;
        goto err_out;
    }
    
    vss = shost_priv(sh);
    vss->sh = sh;
    vss->private_data = NULL;
    vss->data = kzalloc(VSS_SCSI_LOAD_DATA_SIZE, GFP_KERNEL);
    if (vss->data == NULL) {
        printk("kzallocfailed, not enough memory.\n"); 
        ret = -ENOMEM;
        goto err_out;
    }

    if (g_scsi_hook_op->stt) {
        sh->transportt = &vsc_scsi_transport_template;
    }

    mutex_lock(&scsi_if_vss_list_lock);
    list_add(&vss->list, &scsi_if_vss_list);
    mutex_unlock(&scsi_if_vss_list_lock);

    return vss;
err_out:
    if (sh) {
        if (vss->data) {
            kfree(vss->data);
            vss->data = NULL;
        }

        scsi_host_put(sh);
    }

    return ERR_PTR(ret);
}
EXPORT_SYMBOL(vsc_scsi_if_alloc);

/**************************************************************************
 功能描述  : 释放scsi控制句柄。
 参    数  : scsi控制句柄
 返 回 值  : 无
**************************************************************************/
void vsc_scsi_if_do_free(struct vsc_scsi_struct * vss)
{
    if (!vss) {
        return;
    }

    /* 从链表中删除控制结构 */
    list_del(&vss->list);

    vss->private_data = NULL;

    if (vss->data) {
        kfree(vss->data);
        vss->data = NULL;
    }   

    /* 释放内存 */
    scsi_host_put(vss->sh);
}

/**************************************************************************
 功能描述  : 封装的Scsi_Host结构体释放函数
 参    数  : scsi控制句柄
 返 回 值  : 无
**************************************************************************/
void vsc_scsi_if_free(struct vsc_scsi_struct * vss)
{
    if (!vss) {
        return;
    }

    mutex_lock(&scsi_if_vss_list_lock);
    vsc_scsi_if_do_free(vss);
    mutex_unlock(&scsi_if_vss_list_lock);
}
EXPORT_SYMBOL(vsc_scsi_if_free);

/**************************************************************************
 功能描述  : 将vsc的控制句柄设置到vsc scsi if
 参    数  : scsi控制句柄
             私有数据指针
 返 回 值  : 无
**************************************************************************/
int vsc_scsi_if_set_priv(struct vsc_scsi_struct * vss, void *private_data)
{
    if (!vss) {
        return -EINVAL;
    }

    vss->private_data = private_data;

    return 0;
}
EXPORT_SYMBOL(vsc_scsi_if_set_priv);

/**************************************************************************
 功能描述  : 获取设置的vsc控制句柄
 参    数  : scsi控制句柄
 返 回 值  : 私有数据指针
**************************************************************************/
void *vsc_scsi_if_get_priv(struct vsc_scsi_struct * vss)
{
    if (unlikely(!vss)) {
        return NULL;
    }

    return vss->private_data;
}
EXPORT_SYMBOL(vsc_scsi_if_get_priv);

/**************************************************************************
 功能描述  : 获取Scsi_Host句柄
 参    数  : scsi控制句柄
 返 回 值  : scsi host句柄
**************************************************************************/
struct Scsi_Host *vsc_scsi_if_get_host(struct vsc_scsi_struct * vss)
{
    if (unlikely(!vss)) {
        return NULL;
    }

    return vss->sh;
}
EXPORT_SYMBOL(vsc_scsi_if_get_host);

/**************************************************************************
 功能描述  : 删除所有SCSI HOST，以及对应的虚拟设备
 参    数  : 无
 返 回 值  : 0
**************************************************************************/
int vsc_scsi_if_remove_all_host(void)
{
    struct vsc_scsi_struct * vss, *tmp;

    mutex_lock(&scsi_if_vss_list_lock);
    list_for_each_entry_safe(vss, tmp, &scsi_if_vss_list, list) {
        scsi_unblock_requests(vss->sh);
        scsi_remove_host(vss->sh);
        vsc_scsi_if_do_free(vss);
    }
    mutex_unlock(&scsi_if_vss_list_lock);

    return 0;
}

/**************************************************************************
 功能描述  : 调用vsc注册的SCSI HOST卸载函数
 参    数  : 无
 返 回 值  : 加载结果
**************************************************************************/
int vsc_scsi_if_unload_all_host(void)
{
    struct vsc_scsi_struct * vss, *tmp;

    mutex_lock(&scsi_if_vss_list_lock);
    list_for_each_entry_safe(vss, tmp, &scsi_if_vss_list, list) {
        scsi_block_requests(vss->sh);
        if (vss->private_data) {
            g_scsi_hook_op->unload(vss, vss->data, VSS_SCSI_LOAD_DATA_SIZE);
        }
        vss->private_data = NULL;
    }
    mutex_unlock(&scsi_if_vss_list_lock);

    return 0;
}

/**************************************************************************
 功能描述  : 调用vsc注册的SCSI HOST加载函数
 参    数  : 无
 返 回 值  : 加载结果
**************************************************************************/
int vsc_scsi_if_load_all_host(void)
{
    struct vsc_scsi_struct * vss, *tmp;

    mutex_lock(&scsi_if_vss_list_lock);
    list_for_each_entry_safe(vss, tmp, &scsi_if_vss_list, list) {
        if (g_scsi_hook_op->load(vss, vss->data, VSS_SCSI_LOAD_DATA_SIZE) != 0) {
            goto err_out;
        }
    }
    mutex_unlock(&scsi_if_vss_list_lock);

    return 0;
err_out:
	mutex_unlock(&scsi_if_vss_list_lock);
    vsc_scsi_if_unload_all_host();
    return -EFAULT;
}

/**************************************************************************
 功能描述  : 读取/proc/vsc/vsc的处理函数
 参    数  : page: 缓存页面
             start: 起始地址指针
             off:偏移
             eof:是否结束
             data:私有数据
 返 回 值  : 读取数据的长度
**************************************************************************/
#if LINUX_VERSION_CODE > (KERNEL_VERSION(2, 6, 25)) 
static int vsc_scsi_if_ctrl_read(struct seq_file *sfile, void *unused)
{
    struct vsc_scsi_struct * vss, *tmp;
    int host_count = 0;

    seq_printf(sfile, "Vsc statues:\t%s\n", (g_scsi_hook_if_stop) ? "Stopped" : "Running");
    
    mutex_lock(&scsi_if_vss_list_lock);
    list_for_each_entry_safe(vss, tmp, &scsi_if_vss_list, list) {
        host_count++;
    }
    mutex_unlock(&scsi_if_vss_list_lock);
    seq_printf(sfile, "Host count:\t%u\n", host_count); 

    return 0;
}

/**************************************************************************
 功能描述  : 写入/proc/vsc/vsc的处理函数
 参    数  : file: 文件句柄
             buf: 写入的数据
             count:长度
             data:私有数据
 返 回 值  : 写入数据的长度
**************************************************************************/
static ssize_t vsc_scsi_if_ctrl_write(struct file *file, const char __user *user_ptr,
                                  size_t len, loff_t *pos)
{
    char *buffer, *p;
    int err = -EFAULT;

    buffer = (char *)__get_free_page(GFP_KERNEL);
    if (!buffer) {
        return -ENOMEM;
    }

    if (len > PAGE_SIZE)
    {
        len = PAGE_SIZE;
    }
    if (copy_from_user(buffer, user_ptr, len)) {
        goto errout;
    }

    buffer[len -1] = '\0';

    /*
	 * Usage: echo "vsc [cmd]" >/proc/vsc/vsc
	 */
    if (!strncmp("vsc", buffer, 3)) {
        p = buffer + 4;
    }

    free_page((unsigned long)buffer);
    return len;
errout:
    free_page((unsigned long)buffer);
    return err;
}

static int vsc_scsi_if_seq_open_dev(struct inode *inode, struct file *file)
{
#if LINUX_VERSION_CODE < (KERNEL_VERSION(3, 10, 0))
    return single_open(file, vsc_scsi_if_ctrl_read, PDE(inode)->data);
#else
    return single_open(file, vsc_scsi_if_ctrl_read, PDE_DATA(inode));
#endif
}

static struct file_operations g_vsc_scsi_proc_ops = 
{
#if LINUX_VERSION_CODE >= KERNEL_VERSION(2, 6, 27)
    .owner = THIS_MODULE,
#endif
    .open = vsc_scsi_if_seq_open_dev,
    .read = seq_read,
    .write = vsc_scsi_if_ctrl_write,
    .llseek = seq_lseek,
    .release = NULL,
};

#else
int vsc_scsi_if_ctrl_read_old(char *page, char **start, 
	off_t off, int count, int *eof, void *data)
{
    struct vsc_scsi_struct * vss, *tmp;
    int host_count = 0;
    int len = 0;
    len += snprintf((page + len), (count - len), "Vsc statues:\t%s\n", (g_scsi_hook_if_stop) ? "Stopped" : "Running");
    
    mutex_lock(&scsi_if_vss_list_lock);
    list_for_each_entry_safe(vss, tmp, &scsi_if_vss_list, list) {
        host_count++;
    }
    mutex_unlock(&scsi_if_vss_list_lock);
    len += snprintf((page + len), (count - len), "Host count:\t%u\n", host_count); 
    return len;
}

int vsc_scsi_if_ctrl_write_old(struct file *file, const char *buffer, 
		unsigned long count, void *data)
{

    char *buf, *p;
    buf = (char *)__get_free_page(GFP_KERNEL);
    if (!buf) {
        return -ENOMEM;
    }

    if (count > PAGE_SIZE)
    {
        count = PAGE_SIZE;
    }
    if (copy_from_user(buf, buffer, count)) {
        goto errout;
    }

    buf[count -1] = '\0';

    /*
     * Usage: echo "vsc [cmd]" >/proc/vsc/vsc
     */
    if (!strncmp("vsc", buf, 3)) {
        p = buf + 4;
    }

    free_page((unsigned long)buf);
    return count;
errout:
    free_page((unsigned long)buf);
    return count;
}

#endif
/**************************************************************************
 功能描述  : 创建/proc/vsc/vsc文件
 参    数  : 
 返 回 值  : 创建结果
**************************************************************************/
int vsc_scsi_if_create_ctrl_file(void)
{
    struct proc_dir_entry  *proc_file = NULL;
   
#if LINUX_VERSION_CODE > (KERNEL_VERSION(2, 6, 25))   
    proc_file = proc_create_data(VSC_SCSI_IF_PROC_CTL_FILE, S_IRUGO, proc_vsc_root, &g_vsc_scsi_proc_ops, NULL);
    if (!proc_file) {
        return -EFAULT;
    }
#else
    proc_file = create_proc_entry(VSC_SCSI_IF_PROC_CTL_FILE, S_IRUGO, proc_vsc_root);
    if (!proc_file) {
        return -EFAULT;
    }
    proc_file->read_proc=vsc_scsi_if_ctrl_read_old;
    proc_file->write_proc=vsc_scsi_if_ctrl_write_old;
    proc_file->data=NULL;
#endif
    return 0;
}

/**************************************************************************
 功能描述  : 删除/proc/vsc/vsc_scsi_if文件
 参    数  : 
 返 回 值  : 无
**************************************************************************/
int vsc_scsi_inf_remove_ctrl_file(void)
{
    remove_proc_entry(VSC_SCSI_IF_PROC_CTL_FILE, proc_vsc_root);

    return 0;
}

/**************************************************************************
 功能描述  : vsc向vsc scsi if注册回调函数
 参    数  : scsi host 回调函数模板
 返 回 值  : 注册结果
**************************************************************************/
int vsc_scsi_if_register(struct vsc_scsi_host_operation *vsc_hop)
{
    if (!vsc_hop) {
        return -EINVAL;
    }

    if (g_scsi_hook_op) {
        return -EEXIST;
    }

    if (!vsc_hop->load || !vsc_hop->unload || !vsc_hop->sht) {
        return -EINVAL;
    }

    /* 注册回调函数 */
    g_scsi_hook_op = vsc_hop;
    vsc_scsi_if_setup_host_template(vsc_hop->sht);
    vsc_scsi_if_setup_transport_template(vsc_hop->stt);

    atomic_set(&vsc_users, 0);
    vsc_unload_complete = NULL;
    spin_lock_init(&vsc_unload_lock);       

    /* 重新加载SCSI HOST数据 */
    if (vsc_scsi_if_load_all_host())
    {
		g_scsi_hook_op = NULL;
		return -EFAULT;
	}

    /* 设置驱动运行 */
    vsc_scsi_if_scmnd_inc();
    g_scsi_hook_if_stop = 0;

    return 0;
}
EXPORT_SYMBOL(vsc_scsi_if_register);

/**************************************************************************
 功能描述  : vsc注销回调函数
 参    数  : 
 返 回 值  : 无
**************************************************************************/
int vsc_scsi_if_unregister(void)
{
    /* 设置驱动停止运行 */
    g_scsi_hook_if_stop = 1;
    vsc_scsi_if_scmnd_dec();
    /* 卸载SCSI HOST数据 */

    /* 等待中间状态任务处理完成 */
    vsc_scsi_if_wait_scmnd_complete();

    vsc_scsi_if_unload_all_host();

    g_scsi_hook_op = NULL;
    return 0;
}
EXPORT_SYMBOL(vsc_scsi_if_unregister);

/**************************************************************************
 功能描述  : vsc scsi初始化函数
 参    数  : 
 返 回 值  : 初始化结果
**************************************************************************/
static int __init vsc_scsi_if_init( void )
{
    int retval;

    printk(banner);

    /* 创建/proc/vsc目录 */
    proc_vsc_root = proc_mkdir("vsc", NULL);
    if (!proc_vsc_root) {
        printk("create proc directory failed.\n");
        retval = -EFAULT;
        goto errout1;
    }

    /* 创建/proc/vsc/vsc_scsi_if文件，提供状态查询的接口 */
    if (vsc_scsi_if_create_ctrl_file()) {
        printk("create control file failed.\n");
        retval = -EFAULT;
        goto errout2;
    }

    g_scsi_hook_op = NULL;
    g_scsi_hook_if_stop = 1; 
    INIT_LIST_HEAD(&scsi_if_vss_list);

    return 0;

errout2:
    remove_proc_entry("vsc", NULL);
errout1:    
    printk("Virtual storage controller scsi interface driver initialize failed, ret = %d\n", retval);
    return retval;
}

/**************************************************************************
 功能描述  : vsc scsi退出函数
 参    数  : 
 返 回 值  : 无
**************************************************************************/
static void __exit vsc_scsi_if_exit( void )
{
    /* 删除所有SCSC HOST 及其设备 */
    vsc_scsi_if_remove_all_host();

    /* 删除/proc/vsc目录 */
    vsc_scsi_inf_remove_ctrl_file();
    if (proc_vsc_root) {
        remove_proc_entry("vsc", NULL);
    }

    vsc_scsi_if_free_pool();
    printk("Virtual storage controller scsi interface driver unregistered.\n");
    return ;
}


module_init(vsc_scsi_if_init);
module_exit(vsc_scsi_if_exit);

MODULE_DESCRIPTION("Huawei Cloudstorage virtual storage controller scsi interface driver. (build date : "__DATE__" "__TIME__")");
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Huawei Technologies Co., Ltd.");
#ifdef DRIVER_VER
MODULE_VERSION(DRIVER_VER);
#else
MODULE_VERSION("1.0.0");
#endif


