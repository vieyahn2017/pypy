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
from file.controller import FileUploadHandler


define("port", default=9030, help="default run port", type=int)
#define("log_file_prefix", default="lcic.log", help="log file prefix")
options.logging = "debug"
options.log_to_stderr = True



class IndexHandler(web.RequestHandler):

    def get(self):
        self.write("测试首页")


# 初始化HANDLERS
HANDLERS = []

# 测试模块
HANDLERS += [
    (r'/', IndexHandler),
    (r'/test/index', IndexHandler)
]

# file module
HANDLERS += [
    (r'/file/upload', FileUploadHandler.FileUploadHandler),
    (r'/file/ajax', FileUploadHandler.FileUploadAjaxHandler),
    (r'/file/test', FileUploadHandler.FileUploadTestHandler),
]



# APP
class Application(web.Application):
    def __init__(self):
        handlers = HANDLERS
        settings = SETTINGS
        super(Application, self).__init__(handlers, **settings)


# Main入口
if __name__ == '__main__':
    tornado.options.parse_command_line()
    http_server = httpserver.HTTPServer(
        Application(),
        max_buffer_size=MAX_BUFFER_SIZE,
    )
    http_server.listen(options.port)
    app_log.info('Listen on port {0}...'.format(options.port))
    ioloop.IOLoop.current().set_blocking_log_threshold(1)
    ioloop.IOLoop.current().start()
