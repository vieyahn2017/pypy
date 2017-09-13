```bash
redis-benchmark.exe         #基准测试  
redis-check-aof.exe         # aof  
redis-check-dump.exe        # dump  
redis-cli.exe               # 客户端  
redis-server.exe            # 服务器  
redis.windows.conf          # 配置文件

```

# redis-cli
```bash
help
keys *
set key1 "hello"
get key1
set key2 1
INCR key2
INCR key2
get key2
# 增加一个列表记录key3
LPUSH key3 a
LPUSH key3 b
RPUSH key3 c
# 打印列表记录，按从左到右的顺序
LRANGE key3 0 3

# 增加一个哈希记表录key4
redis 127.0.0.1:6379> HSET key4 name "John Smith"
# 在哈希表中插入，email的Key和Value的值
redis 127.0.0.1:6379> HSET key4 email "abc@gmail.com"
# 打印哈希表中，name为key的值
redis 127.0.0.1:6379> HGET key4 name
# 打印整个哈希表
redis 127.0.0.1:6379> HGETALL key4
1) "name"
2) "John Smith"
3) "email"
4) "abc@gmail.com"
```


# 哈希表操作

```bash
# 增加一条哈希表记录key5，一次插入多个Key和value的值
redis 127.0.0.1:6379> HMSET key5 username antirez password P1pp0 age 3
# 打印哈希表中，username和age为key的值
redis 127.0.0.1:6379> HMGET key5 username age
# 打印完整的哈希表记录
redis 127.0.0.1:6379> HGETALL key5
```


redis-server  redis.windows.conf