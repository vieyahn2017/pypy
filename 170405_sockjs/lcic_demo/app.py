# -*- coding:utf-8 -*- 
# --------------------
# Author:		Ken
# Description:	系统入口
# --------------------
import tornado.options
from tornado import httpserver, ioloop, web
from tornado.log import app_log
from tornado.options import define, options

from config import SETTINGS, MAX_BUFFER_SIZE
from analysis.controller import PublishCtrlHandle, PublishLocationUpdateHandle
from analysis.controller.PublishMessageCache import lcic_cache_instance

define("port", default=9030, help="default run port", type=int)
#define("log_file_prefix", default="lcic.log", help="log file prefix")
options.logging = "debug"
options.log_to_stderr = True



class IndexHandler(web.RequestHandler):

    def get(self):
        self.write("测试首页")


# 初始化HANDLERS
HANDLERS = []

HANDLERS += [
    (r'/', IndexHandler),
]

from sockjs.tornado import SockJSRouter

# analysis module
HANDLERS += [
    (r'/analysis/publisher-start', PublishCtrlHandle.PublisherStartHandler), 
]
updater_handler = SockJSRouter(
    PublishLocationUpdateHandle.LocationRealTimeUpdateHandler,
    r'/analysis/updater'  # 实时定位信息推送
)
HANDLERS += updater_handler.urls


# APP
class Application(web.Application):
    def __init__(self):
        handlers = HANDLERS
        settings = SETTINGS
        super(Application, self).__init__(handlers, **settings)


# Main入口
if __name__ == '__main__':
    tornado.options.parse_command_line()
    lcic_cache_instance.lcic_start_cache()
    http_server = httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    app_log.info('Listen on port {0}...'.format(options.port))
    ioloop.IOLoop.current().set_blocking_log_threshold(1)
    ioloop.IOLoop.current().start()
