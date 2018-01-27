# -*- coding: utf-8 -*-

#Asynchronous and non-Blocking I/O
#异步和非阻塞I/O


from tornado.httpclient import httpclient

def synchronous_fetch(url):
	http_client = HTTPClient();
	response = http_client.fetch(url)
	return response.body


#把上面的例子用回调参数重写的异步函数:
from tornado.httpclient import AsyncHTTPClient

def asynchronous_fetch(url, callback):
	http_client = AsyncHTTPClient()
	def handle_response(response):
		callback(response.body)
	http_client.fetch(url, callback=handle_response)
	 

#使用 Future 代替回调:
from tornado.concurrent import Future

def async_fetch_future(url):
	http_client = AsyncHTTPClient()
	my_future = Future()
	fetch_future = http_client.fetch(url)
	fetch_future.add_done_callback(
		lambda f: my_future.set_result(f.result()))
	return my_future


#这里是上面例子的协程版本,和最初的同步版本很像:
from tornado import gen

@gen.coroutine
def fetch_coroutine(url):
	http_client = AsyncHTTPClient()
	response = yield http_client.fetch(url)
	raise gen.Return(response.body)
