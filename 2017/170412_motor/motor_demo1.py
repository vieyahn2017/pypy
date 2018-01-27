#!/usr/bin/env python
#-*-coding:utf-8 -*-

import motor
import tornado.ioloop
import tornado.web
import tornado.ioloop
import tornado.gen

class NewMessageHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        msg = self.get_argument('msg')
        db = self.settings['db']
        result = yield db.messages.insert_one({'msg': msg})
        self.redirect('/')

class MessagesHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        self.write('<a href="/compose">compose a message</a><br>')
        self.write('<ul>')
        db = self.settings['db']
        cursor = db.messages.find().sort([('_id'), -1])
        while(yield cursor.fetch_next()):
            message = cursor.next_object()
            self.write('<li>%s</li>' % message['msg'])
        self.write('</ul>')
        self.finish()

    @tornado.gen.coroutine
    def post(self):
        msg = yield db.messages.find_one({'_id': msg_id})
        prev_future = db.messages.find_one({'_id': {'$lt': msg_id}})
        next_future = db.messages.find_one({'_id': {'$gt': msg_id}})
        previous_msg, next_msg = yield [prev_future, next_future]



###
client = motor.motor_tornado.MotorClient()
db = client.test_database
db = client['test_database']
collection = db.test_collection
collection = db['test_collection']


from tornado.ioloop import IOLoop

def my_callback(result, error):
    print('result %s' % repr(result.inserted_id))
    IOLoop.current().stop()

# document = {'key': 'value'}
# db.test_collection.insert_one(document, callback=my_callback)
# IOLoop.current().start()

def my_callback2(result, error):
    print('result %s error %s' % (repr(result), repr(error)))
    IOLoop.current().stop()

def insert_two_documents():
    db.test_collection.insert_one({'_id': 1}, callback=my_callback2)

# IOLoop.current().add_callback(insert_two_documents)
# IOLoop.current().start()
# IOLoop.current().add_callback(insert_two_documents)
# IOLoop.current().start()
# #result <pymongo.results.InsertOneResult ...> error None
# #result None error DuplicateKeyError(...)


# i = 0
# def do_insert(result, error):
#     global i
#     if error:
#         raise error
#     i += 1
#     if i < 200:
#         db.test_collection.insert_one({'i': i, 'value': i*1000}, callback=do_insert)
#         print('result %s error %s' % (repr(result), repr(error)))
#     else:
#         IOLoop.current().stop()

# db.test_collection.insert_one({'i': i, 'value': i*1000}, callback=do_insert)
# IOLoop.current().start()


@tornado.gen.coroutine
def do_insert2():
    for i in range(20):
        future = db.test_collection.insert_one({'i': i})
        result = yield future

IOLoop.current().run_sync(do_insert2)