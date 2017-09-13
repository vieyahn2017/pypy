# -*- coding: utf-8 -*-
import redis

class Task():
    def __init__(self):
        self.rcon = redis.StrictRedis(host='localhost', db=5)
        self.queue = 'task:prodcons:queue'

    def listen_task(self):
        while True:
            task = self.rcon.blpop(self.queue, 0 )[1]
            print "task get" ,task

if __name__ == "__main__":
    print "listen task queue"
    Task().listen_task()

#生产消费模式
#主要使用了redis提供的blpop获取队列数据，如果队列没有数据则阻塞等待，也就是监听。