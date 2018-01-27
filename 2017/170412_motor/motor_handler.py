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


db = motor.motor_tornado.MotorClient().test

application = tornado.web.Application(
    [
        (r'/compose', NewMessageHandler),
        (r'/', MessagesHandler)
    ],
    db=db
)

print('Listening on http://localhost:8888')
application.listen(8888)
tornado.ioloop.IOLoop.instance().start()
