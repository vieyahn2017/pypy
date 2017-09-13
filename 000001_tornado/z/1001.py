# -*- coding: utf-8 -*- 
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("Hello World")

def make_app():
	return tornado.web.Application([
		(r"/", MainHandler),
	])

if __name__=="__main__":
	app=make_app()
	app.listen(8888)
	tornado.ioloop.IOLoop.current().start()


"""

Tornado is a Python web framework and asynchronous networking library, 
	originally developed at FriendFeed. 
By using non-blocking network I/O, Tornado can scale to tens of thousands of 
	open connections, making it ideal for long polling, WebSockets, 
	and other applications that require a long-lived connection to each user.
Tornado 是一个Python web框架和异步网络库 起初由 FriendFeed 开发. 
通过使用非阻塞网络I/O, Tornado 可以支持上万级的连接，
处理 长连接, WebSockets, 和其他 需要与每个用户保持长久连接的应用.


Tornado can be roughly divided into four major components:

A web framework (including RequestHandler which is subclassed to create 
	web applications, and various supporting classes.	)
Client-and Server-side implementions of HTTP (HTTPServer and AsyncHTTPClient)
An asynchronos networking library including the classes IOLoop and IOStream,
	which serve as the building blocks for the HTTP components and 
	can also be used to implement other protocols.
A coroutine library(tornado.gen) which allows asynchronos code to be written
	in a more straightforward way than chaining callbacks.
	
Tornado 大体上可以被分为4个主要的部分:
web框架 (包括创建web应用的 RequestHandler 类，还有很多其他支持的类).
HTTP的客户端和服务端实现 (HTTPServer and AsyncHTTPClient).
异步网络库 (IOLoop and IOStream), 为HTTP组件提供构建模块，也可以用来实现其他协议.
协程库 (tornado.gen) 允许异步代码写的更直接而不用链式回调的方式.


The Tornado web framework and HTTP server together offer a full-stack alternative to WSGI. 
While it is possible to use the Tornado web framework in a WSGI container (WSGIAdapter), 
or use the Tornado HTTP server as a container for other WSGI frameworks (WSGIContainer), 
each of these combinations has limitations and to take full advantage of Tornado 
you will need to use the Tornado’s web framework and HTTP server together.

Tornado web 框架和HTTP server 一起为 WSGI 提供了一个全栈式的选择. 
在WSGI容器 (WSGIAdapter) 中使用Tornado web框架或者
使用Tornado HTTP server 作为一个其他WSGI框架(WSGIContainer)的容器,
这样的组合方式都是有局限性的. 
为了充分利用Tornado的特性,你需要一起使用Tornado的web框架和HTTP server.
"""
