# -*- coding:utf-8 -*- 
# --------------------
# Author:       
# Description:   
# --------------------

MAX_BUFFER_SIZE = 4 * 1024**3 # 4GB

import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print __file__
print BASE_DIR
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates")  # 模板目录
STATIC_PATH = os.path.join(BASE_DIR, "static")  # 静态资源目录
UPLOAD_PATH = os.path.join(STATIC_PATH, "uploads")

# Postgres配置
# POSTGRES_HOST = "121.42.154.40"
POSTGRES_HOST = "127.0.0.1"
POSTGRES_USER = "test"
POSTGRES_DB = "test"
POSTGRES_PWD = "test"
POSTGRES_PORT = 5432

# MongoDB配置
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

# SETTINGS
SETTINGS = dict(
    template_path=TEMPLATE_PATH,
    static_path=STATIC_PATH,
    cookie_secret="MmvPLn19QXqz83Pq3miVtUwYSA6oi0YCuUI26RUA/LU=",
    xsrf_cookies=True,
    login_url="/auth/login",
    # debug=True,
    ui_modules={
    }
)


# Redis配置
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_URL = 'redis://@127.0.0.1:6379'


class RedisExpire(object):
    def __init__(self):
        pass

    SECOND_EXPIRE = 5  # 5秒释放
    MINUTE_EXPIRE = 60  # 1分钟释放
    HOUR_EXPIRE = 60 * 60  # 1小时释放
    DAY_EXPIRE = 24 * 60 * 60   # 1天释放


# CACHE KEY
LCIC_CACHE_KEY = 'lcic_cache:{0}'