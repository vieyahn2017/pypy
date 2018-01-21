# -*- coding:utf-8 -*- 
# --------------------
# Author:		
# Description:	数据库连接
# --------------------

import redis
# import queries
from pymongo import MongoClient

import db.tornpg
from config import (POSTGRES_HOST, POSTGRES_PORT,
                    POSTGRES_USER, POSTGRES_DB,
                    POSTGRES_PWD, REDIS_HOST,
                    REDIS_PORT, REDIS_DB,
                    MONGODB_HOST, MONGODB_PORT,
                    REDIS_URL)
from config import RedisExpire


# Postgres connect user queries.
# pg_uri = queries.uri(POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PWD)
# pg_session = queries.Session(
#     uri=pg_uri,
#     pool_max_size=20
# )
# #
# pg_tornado_session = queries.TornadoSession(
#     uri=pg_uri,
#     pool_max_size=20
# )

# Postgres connection user tornpg
psdb = db.tornpg.Connection(
    host=POSTGRES_HOST, database=POSTGRES_DB,
    user=POSTGRES_USER, password=POSTGRES_PWD, port=POSTGRES_PORT
)

# Redis connection
rsdb = redis.StrictRedis.from_url(REDIS_URL)


class RedisManager(object):
    def __init__(self):
        self.psredis = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    # 保存key-value值
    # expire的单位是毫秒
    # 参数config中的时效配置
    def save_data(self, key, info, px=RedisExpire.MINUTE_EXPIRE):
        self.psredis.set(key, info, px)

    # 获取redis中key对应的value
    # key是键值
    def get_data(self, key):
        return self.psredis.get(key)

    # 获取redis中key对应的value
    # expire的单位是毫秒
    # 参数config中的时效配置
    # key是键值
    def save_list(self, key, values, px=RedisExpire.MINUTE_EXPIRE):
        self.psredis.lpush(key, values, px)

    # 根据name删除redis中的任意数据类型
    def del_data(self, *key):
        self.psredis.delete(key)


redisManager = RedisManager()


# rsdb = redisManager.psredis


class MongoManager(object):
    def __init__(self):
        client = MongoClient(MONGODB_HOST, MONGODB_PORT)
        self.mongodb = client['lcic']


# mongoManager = MongoManager()























