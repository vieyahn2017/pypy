#!/usr/bin/env/env python
#-*-coding:utf-8 -*-
import pika
import sys

connection =pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='messages2', type='direct')

routings = sys.argv[1:]
if not routings:
    routings = ['info']


result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
for routing in routings:
    channel.queue_bind(exchange='messages2', 
                       queue=queue_name,
                       routing_key=routing)

def callback(ch, method, properties, body):
    print "[x] received %r" % (body,)


channel.basic_consume(callback, queue=queue_name, no_ack=False)

print ' [*] Waiting for messages. To exit press CTRL+C'
channel.start_consuming()

# # worker.py
