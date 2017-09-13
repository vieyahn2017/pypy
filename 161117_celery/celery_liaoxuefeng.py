#!/usr/bin/env python
# coding:utf-8

import requests
import time


from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/1')


@app.task
def sendmail(mail):
    print('sending mail to %s...' % mail['to'])
    time.sleep(2.0)
    print('mail sent.')
 
#  celery worker -A tasks --loglevel=info

# send task:
from tasks import sendmail
sendmail.delay(dict(to='celery@python.org'))