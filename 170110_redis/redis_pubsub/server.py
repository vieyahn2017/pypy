# -*- coding: utf-8 -*-

import redis
import random
import logging

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
from tornado.options import define,options

define("port", default=8000, help="run on the given port", type=int)

rcon = redis.StrictRedis(host='localhost', db=5)
prodcons_queue = 'task:prodcons:queue'
pubsub_channel = 'task:pubsub:channel'

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        html = """
            <br>
            <center><h3>Redis Message Queue</h3>
            <br>
            <a href="/prodcons">生产消费者模式</a>
            <br>
            <br>
            <a href="/pubsub">发布订阅者模式</a>
            </center>
                """
        self.write(html)

class ProdconsHandler(tornado.web.RequestHandler):
    def get(self):
        elem = random.randrange(10)
        rcon.lpush(prodcons_queue, elem)
        logging.info("lpush {} -- {}".format(prodcons_queue, elem))
        self.redirect('/')

class PubsubHandler(tornado.web.RequestHandler):
    def get(self):
        ps = rcon.pubsub()
        ps.subscribe(pubsub_channel)
        elem = random.randrange(10)
        rcon.publish(pubsub_channel, elem)
        logging.info("publish {} -- {}".format(pubsub_channel, elem))
        self.redirect('/')

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers =[
        (r"/", IndexHandler),
        (r"/pubsub", PubsubHandler),
        (r"/prodcons", ProdconsHandler),
    ], debug= True)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()