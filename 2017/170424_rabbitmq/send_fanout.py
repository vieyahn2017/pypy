#!/usr/bin/env/env python
#-*-coding:utf-8 -*-
import pika

connection =pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='messages', type='fanout')

channel.basic_publish(exchange="messages", routing_key='', body="hello world")
print "[x] sent 'hello world"
channel.close()

# # send.py
