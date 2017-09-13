# -*- coding: utf-8 -*-

#Coroutines
#协程


from tornado import gen

@gen.coroutine
def fetch_coroutine(url):
	http_client = AsyncHTTPClient()
	response = yield http_client(url)
    # 在Python 3.3之前, 在generator中是不允许有返回值的
    # 必须通过抛出异常来代替.
    # 就像 raise gen.Return(response.body).
	return response.body



#下面是一个协程装饰器内部循环的简单版本:

#tornado.gen.Runner
def run(self):
	#send(x) makes the current yield return x
	# It returns when the next yield is reached
	future = self.gen.send(self.next)
	def callback(f):
		self.next = f.result()
		self.run()
	future.add_done_callback(callback)





#协程模式
#结合 callback

@gen.coroutine
def call_task():
    # 注意这里没有传进来some_function.
    # 这里会被Task翻译成
    #   some_function(other_args, callback=callback)
    yield gen.Task(some_function, other_args)




#调用阻塞函数
thread_pool = ThreadPoolExecutor(4)

@gen.coroutine
def call_blocking():
    yield thread_pool.submit(blocking_func, args)




#并行
#协程装饰器能识别列表或者字典对象中各自的 Futures, 并且并行的等待这些 Futures :

@gen.coroutine
def parallel_fetch(url1,url2):
	resp1, resp2 = yield [http_client.fetch(url1), http_client.fetch(url2)]

@gen.coroutine
def parallel_fetch_many(urls):
	response = yield [http_client.fetch(url) for url in urls]
	# 响应是和HTTPResponses相同顺序的列表

@gen.coroutine
def parallel_fetch_dict(urls):
	response = yield {url:http_client.fetch(url) for url in urls}
	# 响应是一个字典 {url: HTTPResponse}





#交叉存取
@gen.coroutine
def get(self):
	fetch_future = self.fetch_next_chunk()
	while True:
		chunk = yield fetch_future
		if chunk is None:break
		self.write(chunk)
		fetch_future = self.fetch_next_chunk()
		yield self.flush()




#循环
#下面是一个使用 Motor 的例子:

import motor
db = motor.MotorClient().test

@gen.coroutine
def loop_example(collection):
	cursor = db.collection.find()
	while (yield cursor.fetch_next):
		doc = cursor.next_object()





#在后台运行
@gen.coroutine
def minute_loop():
    while True:
        yield do_something()
        yield gen.sleep(60)

# Coroutines that loop forever are generally started with
# spawn_callback().
IOLoop.current().spawn_callback(minute_loop)



@gen.coroutine
def minute_loop2():
    while True:
        nxt = gen.sleep(60)   # 开始计时.
        yield do_something()  # 计时后运行.
        yield nxt             # 等待计时结束.