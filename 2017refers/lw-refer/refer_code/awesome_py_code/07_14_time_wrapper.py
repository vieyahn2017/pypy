#!/usr/bin/python  
#-*-coding:utf-8-*-

from functools import wraps
import time

def time_it(func):
	@wraps(func)
	def decorate(*args, **kwargs):
		t0 = time.time()
		result = func(*args, **kwargs)
		t = time.time() - t0
		print("{0}{1} = {2} Total time: {3} sec.".format(func.func_name, args, result, t))
		return result
	return decorate

@time_it
def foo(a, b, c):
	return a + b + c

foo(1, 2, 3)
