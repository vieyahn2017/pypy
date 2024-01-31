#!/usr/bin/env python
#-*-coding:utf-8 -*-
# @author:yanghao
# @created:20170523  split from webservices
## Description: BaseServiceHandler

from tornado.web import RequestHandler, asynchronous
# from tornado.gen import coroutine, Return
# from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPResponse, HTTPError
from tornado.log import app_log

from handlers import BaseHandler, Route

class BaseServiceHandler(BaseHandler):

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header("Access-Control-Allow-Headers", 'Content-Type')
        self.set_header('Access-Control-Allow-Methods', 'PUT, DELETE, POST, GET')
        self.set_header('Access-Control-Allow-Credentials',  "true")

    @asynchronous
    def options(self):
        self.set_status(204)
        self.finish()

    # def write(self, chunk):
    #     """暂时解决跨域，引入这个header"""
    #     self.set_header('Access-Control-Allow-Origin', '*')
    #     super(BaseHandler, self).write(chunk)

    def write_ok(self, msg="success"):
        self.write({"code": 1, "msg": msg})

    def write_failure(self, msg='failed'):
        self.write({"code": 0, "msg": msg})

    def parse_fetch(self, item):
        if item.get('code') in [404, 500]: # 404, 500
            #self.write_error(status_code=item.get('code'), exc_info=item)
            # item = {'url': 'http://10.0.0.252:30002/api/v1/compute/az', 'msg': '[Errno 111] Connection refused', 'code': 404}
            self.write(item)
            self.finish()
            # 目前 RuntimeError: Cannot write() after finish()
            return []
        if item.get("rows"):
            return item.get("rows")



###############################3

import inspect

def _get_class_that_defined_method(meth):
    for cls in inspect.getmro(meth.__self__.__class__):
        if meth.__name__ in cls.__dict__: return cls
    return None

class CorsMixin(object):

    CORS_ORIGIN = None
    CORS_HEADERS = None
    CORS_METHODS = None
    CORS_CREDENTIALS = None
    CORS_MAX_AGE = 86400
    CORS_EXPOSE_HEADERS = None

    def set_default_headers(self):
        if self.CORS_ORIGIN:
            self.set_header("Access-Control-Allow-Origin", self.CORS_ORIGIN)

        if self.CORS_EXPOSE_HEADERS:
            self.set_header('Access-Control-Expose-Headers', self.CORS_EXPOSE_HEADERS)

    @asynchronous
    def options(self, *args, **kwargs):
        if self.CORS_HEADERS:
            self.set_header('Access-Control-Allow-Headers', self.CORS_HEADERS)
        if self.CORS_METHODS:
            self.set_header('Access-Control-Allow-Methods', self.CORS_METHODS)
        else:
            self.set_header('Access-Control-Allow-Methods', self._get_methods())
        if self.CORS_CREDENTIALS != None:
            self.set_header('Access-Control-Allow-Credentials',
                "true" if self.CORS_CREDENTIALS else "false")
        if self.CORS_MAX_AGE:
            self.set_header('Access-Control-Max-Age', self.CORS_MAX_AGE)

        if self.CORS_EXPOSE_HEADERS:
            self.set_header('Access-Control-Expose-Headers', self.CORS_EXPOSE_HEADERS)

        self.set_status(204)
        self.finish()

    def _get_methods(self):
        supported_methods = [method.lower() for method in self.SUPPORTED_METHODS]
        #  ['get', 'put', 'post', 'patch', 'delete', 'options']
        methods = []
        for meth in supported_methods:
            instance_meth = getattr(self, meth)
            if not meth:
                continue
            handler_class = _get_class_that_defined_method(instance_meth)
            if not handler_class is RequestHandler:
                methods.append(meth.upper())

        return ", ".join(methods)


class BaseServiceHandler_yh(CorsMixin, BaseHandler):
    """我找的跨域的实现，挺繁琐，还是用之前的吧"""
    CORS_ORIGIN = '*'
    CORS_HEADERS = 'Content-Type'
    CORS_METHODS = 'PUT, DELETE'
    CORS_CREDENTIALS = True
    CORS_MAX_AGE = None
    CORS_EXPOSE_HEADERS = 'Location'






