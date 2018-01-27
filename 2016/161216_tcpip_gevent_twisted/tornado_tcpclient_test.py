# -*- coding: utf-8 -*- 

# tornado 最近的4.0版本新增的 tornado.tcpclient 模块，可以简化客户端的编写。
#下面是随手写的个例子，向本地的 Redis 服务器调用 "set a 1" 和 "get a"，并输出结果，整个过程是异步的：

from contextlib import closing 
from tornado.gen import coroutine 
from tornado.httpserver import HTTPServer 
from tornado.ioloop import IOLoop 
from tornado.tcpclient import TCPClient 
from tornado.web import Application, RequestHandler 

class HomeHandler(RequestHandler): 
	@coroutine 
	def get(self): 
		self.set_header('Content-Type', 'text/plain') 
		client = TCPClient() 
		stream = yield client.connect('127.0.0.1', 6379) 

		with closing(stream): 
			stream.write('set a 1\r\n') 
			data = yield stream.read_until('\r\n') 
			self.write(data) 
			self.flush() 
			stream.write('get a\r\n') 
			data = yield stream.read_until('\r\n') 
			self.write(data) 
			data = yield stream.read_until('\r\n') 
			self.finish(data) 

def main(): 
	application = Application( [('/', HomeHandler)], debug=True) 
	http_server = HTTPServer(application) 
	http_server.listen(8888) 
	IOLoop.instance().start() 

if __name__ == "__main__": 
	main()