#!/usr/bin/env python
#-*-coding:utf-8 -*-

import motor
import tornado.ioloop
import tornado.web
import tornado.ioloop
import tornado.gen


client = motor.motor_tornado.MotorClient()
db = client.test_database
db = client['test_database']
collection = db.test_collection
collection = db['test_collection']


from tornado.ioloop import IOLoop

@tornado.gen.coroutine
def f_insert_many():
    yield db.test.insert_many(({'i': i} for i in range(10000)))
    count = yield db.test.count()
    print("final conut: %d" % count)

#IOLoop.current().run_sync(f_insert_many)

from pprint import pprint

@tornado.gen.coroutine
def f1():
    bulk = db.test2.initialize_ordered_bulk_op()
    bulk.find({}).remove()
    bulk.insert({'_id': 1})
    bulk.insert({'_id': 2})
    bulk.insert({'_id': 3})
    bulk.find({'_id': 1}).update({'$set': {'foo': 'bar'}})
    bulk.find({'_id': 4}).upsert().update({'$inc': {'j': 1}})
    bulk.find({'j': 1}).replace_one({'j': 2})
    result = yield bulk.execute()
    pprint(result)

IOLoop.current().run_sync(f1)
