# -*- coding: utf-8 -*- 

# gevent中带有WSGI的server实现。。。
# 所以，可以很方便的利用gevent来开发http服务器。。。
# 例如如下代码，采用gevent加tornado的方式。。。。
#（tornado其实自带的有I/O循环，但是用gevent可以提高其性能。。）

from gevent import monkey;
monkey.patch_all()

from gevent.wsgi import WSGIServer
import gevent
import tornado
import tornado.web
import tornado.wsgi

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello world (tornado)")

def app(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ["<b>hello world</b>"]

if __name__ == "__main__":
    app_tor = tornado.wsgi.WSGIApplication(handlers=[(r"/", IndexHandler)])
    #server = gevent.wsgi.WSGIServer(("", 8000), app)
    server = gevent.wsgi.WSGIServer(("", 8002), app_tor)
    # 两个都可以运行，一个是调用自己简单写的app，一个是调用tornado的app
    server.serve_forever()