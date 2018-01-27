#!/usr/bin/env python
# coding:utf-8

import requests
import time


# def func(urls):
#     start = time.time()
#     for url in urls:
#         resp = requests.get(url)
#         print resp.status_code
#     print "It took", time.time() - start, "seconds"

# def func(urls):   
#     for url in urls:
#         start = time.time()
#         resp = requests.get(url)
#         print resp.status_code
#         print url, "  took", time.time() - start, "seconds"


from celery import Celery

# pip install celery
# pip install celery-with-redis 要装这个！！！

# app = Celery('celery_blog', broker='redis://localhost:6379/1')
from celery_config import app

@app.task
def fetch_url(url):
    resp = requests.get(url)
    print resp.status_code
 
def func(urls):
    for url in urls:
        fetch_url.delay(url)


# 在3个终端中启动：
# 第一个终端，运行 redis-server
# 第二个终端，运行 celery worker -A celery_blog -l info -c 5 ，通过输出可以看到 celery 成功运行。
# 第三个终端，运行脚本 python celery_blog.py

if __name__ == "__main__":
    func(["http://oneapm.com", "http://jd.com", "https://taobao.com", "http://baidu.com", "http://microsoft.com"])