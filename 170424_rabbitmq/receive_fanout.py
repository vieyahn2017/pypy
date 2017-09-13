#!/usr/bin/env/env python
#-*-coding:utf-8 -*-
import pika

connection =pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='messages', type='fanout')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='messages', queue=queue_name)

def callback(ch, method, properties, body):
    print "[x] received %r" % (body,)


channel.basic_consume(callback, queue=queue_name, no_ack=False)

print ' [*] Waiting for messages. To exit press CTRL+C'
channel.start_consuming()

# # worker.py
