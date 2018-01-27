#!/usr/bin/env python
#-*-coding:utf-8 -*-

import datetime
import motor
import tornado.ioloop
import tornado.web
from tornado.ioloop import IOLoop
import tornado.gen
from pymongo.cursor import CursorType

import functools

client = motor.motor_tornado.MotorClient()
db = client.test_database

@tornado.gen.coroutine
def tail_example(loop_instance):
    results = []
    collection = db.my_capped_collection
    cursor = collection.find(cursor_type=CursorType.TAILABLE) #, await_data=True)
    while True:
        yield tornado.gen.Task(loop_instance.add_timeout, datetime.timedelta(seconds=1))
        cursor = collection.find(cursor_type=CursorType.TAILABLE) #, await_data=True)

    if(yield cursor.fetch_next):
        results.append(cursor.next_object())
        print results

IOLoop.current().run_sync(
    functools.partial(tail_example,
                      IOLoop.current())
    )

# 没有运行成功，官方代码如下，上面是我修改的
"""
@gen.coroutine
def tail_example():
    results = []
    collection = db.my_capped_collection
    cursor = collection.find(cursor_type=CursorType.TAILABLE, await_data=True)
    while True:
        if not cursor.alive:
            now = datetime.datetime.utcnow()
            # While collection is empty, tailable cursor dies immediately
            yield gen.Task(loop.add_timeout, datetime.timedelta(seconds=1))
            cursor = collection.find(cursor_type=CursorType.TAILABLE, await_data=True)

        if (yield cursor.fetch_next):
            results.append(cursor.next_object())
            print results
"""

