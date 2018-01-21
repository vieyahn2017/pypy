# -*- coding:utf-8 -*- 
# --------------------
# Author:		gxm1015@qq.com
# Description:	
# --------------------
import time


def exe_time(func):
    def decorator(*args, **kwargs):
        start = time.time()
        back = func(*args, **kwargs)
        print('Function name:{0} {1}'.format(func.__name__, time.time() - start))
        return back
    return decorator
