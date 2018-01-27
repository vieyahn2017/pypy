# -*- coding:utf-8 -*- 
# --------------------
# Author:		gxm1015@qq.com
# Description:	
# --------------------
from .dbManager import rsdb
from functools import wraps
from tornado.escape import json_decode, json_encode
from config LCIC_CACHE_KEY


class CommonCache(object):
    """A common redis cache class."""
    def __init__(self):
        self.server = rsdb

    def set(self, key, value, ex=60):
        rsdb.set(key, value, ex)

    def get(self, key):
        return self.server.get(key)

cache = CommonCache()


def cached(timeout=5*60, key=LCIC_CACHE_KEY):
    """
    A decorators can cache model result to redis.
    :param timeout: sec
    :param key:
    :return:
    """
    def cache_to_redis(fun):
        @wraps(fun)
        def decorators(self, *args, **kwargs):
            cache_key = key.format(
                self.__class__.__name__.lower() + ':' + fun.__name__
            )
            cache_value = rsdb.get(cache_key)
            if cache_value is not None:
                return json_decode(cache_value)
            cache_value = fun(self, *args, **kwargs)
            rsdb.set(
                cache_key,
                json_encode(cache_value),
                ex=timeout
            )
            return cache_value
        return decorators
    return cache_to_redis
