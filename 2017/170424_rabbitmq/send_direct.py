#!/usr/bin/env/env python
#-*-coding:utf-8 -*-
import pika

connection =pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost'))
channel = connection.channel()

# 这里设置为direct表示要根据设定的路由键来发送消息。
channel.exchange_declare(exchange='messages2', type='direct')

routings = ['info', 'warning', 'error']

for routing in routings:
    message = ' %s message' % routing
    print message
    channel.basic_publish(exchange="messages2", 
                         routing_key=routing, 
                         body=message)

channel.close()

# # send.py
