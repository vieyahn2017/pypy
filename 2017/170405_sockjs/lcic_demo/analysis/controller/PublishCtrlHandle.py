# -*- coding:utf-8 -*- 
# --------------------
# Author:		gxm1015@qq.com
# Description:	Vehicle info message real time push to client.
# --------------------
import functools
import tornado.ioloop
from concurrent.futures import ThreadPoolExecutor
from tornado import gen
from tornado.concurrent import app_log
from tornado.concurrent import run_on_executor
from tornado.web import asynchronous, RequestHandler

from .PublishLocationUpdateHandle import LocationRealTimeUpdateHandler
from .PublishMessageCache import (gps_queue_instance,
                                  lcic_cache_instance)


class PublisherStartHandler(RequestHandler):
    executor = ThreadPoolExecutor(1)
    started = False

    @asynchronous
    @gen.coroutine
    def get(self, *args, **kwargs):
        if not PublisherStartHandler.started:
            tornado.ioloop.IOLoop.instance().add_callback(
                functools.partial(self.get_msg_from_redis_queue)
            )
            PublisherStartHandler.started = True
            self.finish({"state": 0})
        else:
            self.finish({"state": 1})

    @run_on_executor
    def get_msg_from_redis_queue(self):
        while True:
            try:
                msg_json = gps_queue_instance.pop()
                if not msg_json:
                    continue
                app_log.debug(msg_json)
                msg_dict = lcic_cache_instance.get_vehicle_by_json(msg_json)
                if msg_dict:
                    LocationRealTimeUpdateHandler.msg_send_handler(msg_dict)
            except Exception as e:
                import traceback
                print(traceback.print_exc())
                app_log.error('Error: get_msg_from_redis_queue: {0}'.format(e))
                continue

