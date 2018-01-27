# -*- coding: utf-8 -*- 

from contextlib import contextmanager
from random import random
 
DEFAULT_EXPIRES = 15
DEFAULT_RETRIES = 5
 
@contextmanager
def dist_lock(key, client):
    key = 'lock_%s' % key
 
    try:
        _acquire_lock(key, client)
        yield
    finally:
        _release_lock(key, client)
 
def _acquire_lock(key, client):
    for i in xrange(0, DEFAULT_RETRIES):
        get_stored = client.get(key)
        if get_stored:
            print '%s is ' % key, get_stored
            sleep_time = (((i+1)*random()) + 2**i) / 5
            print 'Sleeipng for %s' % (sleep_time)
            time.sleep(sleep_time)
        else:
            stored = client.set(key, 1)
            client.expire(key,DEFAULT_EXPIRES)
            # return
    # raise Exception('Could not acquire lock for %s' % key)
 
def _release_lock(key, client):
    client.delete(key)
    print key, ' has deleted'



import redis

redis_client = redis.Redis(host='localhost',port=6379,db=0)


# test
with dist_lock('a', redis_client) : pass
with dist_lock('c', redis_client) : pass

# 去redis测试
# set lock_a '250'
# get lock_b
# get lock_c



# 原始代码，我上面测试的有改动
from contextlib import contextmanager
from random import random
 
DEFAULT_EXPIRES = 15
DEFAULT_RETRIES = 5
 
@contextmanager
def dist_lock(key, client):
    key = 'lock_%s' % key
 
    try:
        _acquire_lock(key, client)
        yield
    finally:
        _release_lock(key, client)
 
def _acquire_lock(key, client):
    for i in xrange(0, DEFAULT_RETRIES):
        get_stored = client.get(key)
        if get_stored:
            sleep_time = (((i+1)*random()) + 2**i) / 2.5
            print 'Sleeipng for %s' % (sleep_time)
            time.sleep(sleep_time)
        else:
            stored = client.set(key, 1)
            client.expire(key,DEFAULT_EXPIRES)
            return
    raise Exception('Could not acquire lock for %s' % key)
 
def _release_lock(key, client):
    client.delete(key)





# redis_connpool = redis.ConnectionPool(host='localhost', port=6379, db=0, socket_timeout=4)

# class Redis_Client(object):
#     def __init__(self):
#         self.pool = redis.ConnectionPool(host='localhost', port=6379, db=0, socket_timeout=4)

#     def get(self, key):
#         result = redis.Redis(connection_pool=self.pool)
#         return result.get(key)