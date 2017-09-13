#-*- coding: utf-8 -*- 


import socket 
import threading 

def scan(port):  
    s = socket.socket()  
    s.settimeout(0.1)  
    if s.connect_ex(('localhost', port)) == 0:  
        print port, 'open'  
    s.close() 

def main_version1(): # 普通多线程版本
    threads = [threading.Thread(target=scan, args=(i,)) for i in xrange(1,3000)]
    map(lambda x:x.start(), threads)
    # threads = [threading.Thread(target=scan, args=(i,)) for i in xrange(1,65536)]
    # 开65536个线程，不想活了是吧


from Queue import Queue

def main_version2(): # 多线程+队列版本  # 这里开500个线程，不停的从队列取任务来做。
    def worker():
        while not q.empty():
            port = q.get()
            try:
                scan(port)
            finally:
                q.task_done()
    q = Queue()
    map(q.put, xrange(1,65535))
    threads = [threading.Thread(target=worker) for i in xrange(500)]
    map(lambda x:x.start(), threads)
    q.join()



# multiprocessing+队列版本
# 总不能开65535个进程吧？还是用生产者消费者模式

import multiprocessing  

def main_version3():
    def worker(q):  
        while not q.empty():  
            port = q.get()  
            try:  
                scan(port)  
            finally:  
                q.task_done()  

    q = multiprocessing.JoinableQueue()  
    map(q.put,xrange(1,65535))  
    jobs = [multiprocessing.Process(target=worker, args=(q,)) for i in xrange(100)]  
    map(lambda x:x.start(),jobs)  
    # 注意这里把队列作为一个参数传入到worker中去，因为是process safe的queue，不然会报错。
    # 还有用的是JoinableQueue()，顾名思义就是可以join()的。



from gevent import monkey; monkey.patch_all();  
import gevent  

def main_version4():
    threads = [gevent.spawn(scan, i) for i in xrange(1,65536)]  
    gevent.joinall(threads) 


## 3,4  都有问题
if __name__ == '__main__':  
    main_version2()