#!/usr/bin/env python
#-*-coding:utf-8 -*-

from __future__ import absolute_import

from bson import ObjectId
from schematics.types import StringType, IntType, BooleanType
from schematics.types.compound import ListType, DictType
from schematics.contrib.mongo import ObjectIdType

from mongo_orm import BaseMongoModel, context


class BaseAPIModel(BaseMongoModel):
    def __init__(self, *args, **kwargs):
        super(BaseAPIModel, self).__init__(*args, **kwargs)
        default_db = context['dbconn'].test
        self.set_db(kwargs.pop('db', default_db))

class APiModel(BaseAPIModel):
    name = StringType()
    url = StringType()
    method = StringType()
    description = StringType()
    paramsIdList = ListType(StringType)
    responseIdList = ListType(StringType)
    paramsDemo = StringType()
    responseDemo = StringType()

    _id = ObjectIdType(serialize_when_none=False)
    MONGO_COLLECTION = 'api'



import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.options
import tornado.log

tornado.options.define("port", default=9000, help="run on the given port", type=int)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello, world!")

class APiModelTestHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        """应该是的model的属性，这边加一个，方便点"""
        return context['dbconn'].test

    @tornado.gen.coroutine
    def get(self):
        query = {}
        _id = self.get_argument('id', None)
        if _id:
            query = {"_id": ObjectId(_id)}
        cursor = APiModel.get_cursor(self.db, query)
        objects = yield APiModel.find(cursor)
        if objects:
            objects_list = [obj.to_primitive() for obj in objects]
            self.write({"code": 1, "msg": "ok", "rows": objects_list})
        else:
            self.write({"code": -1, "msg": "failure", "rows": []})


    @tornado.gen.coroutine
    def post(self):
        """ init """
        yield APiModel({
            "name": "api_name", 
            "url": "api_url", 
            "method": "GET", 
            "description": "接口描述", 
            "paramsIdList": ["5967155cf0881b4acb2dd5e6", "5967155cf0881b4acb2dd5e7"] ,
            "responseIdList": ["5967155cf0881b4acb2dd5e6", "5967155cf0881b4acb2dd5e7"] , 
            "paramsDemo": """{\n  \"uuid\": \"63211109-c566-4b8e-b49f-2a9816df2afa\",\n  \"action\": 1\n}""",
            "responseDemo":"""{\n    \"msg\":\"\",\n    \"code\": 1,\n    \"rows\": []\n}"""
        }).save()
        self.write({"code": 1, "msg": "ok", "rows": []})


class MyApplication(tornado.web.Application):
    def __init__(self):
        handlers =[
                    (r"/", IndexHandler),
                    (r"/api", APiModelTestHandler),
                    ]
        setting = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
            )
        tornado.web.Application.__init__(self, handlers, **setting)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(MyApplication())
    http_server.listen(tornado.options.options.port)
    tornado.log.app_log.info("the app is running at: %s" % tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()
