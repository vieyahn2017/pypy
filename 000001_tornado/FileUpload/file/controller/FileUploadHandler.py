# -*- coding:utf-8 -*-
# --------------------
# Author:		Yh001
# Description:
# --------------------

import binascii
import os.path
import uuid

import tornado.web
from tornado.web import authenticated, stream_request_body
from tornado.httpclient import HTTPError

from config import UPLOAD_PATH

from db.dbManager import psdb
from ..model.file_streamer import ps_save2db
from ..utils.post_streamer import PostDataStreamer


is_print_test = True

class MyPostDataStreamer(PostDataStreamer):
    percent = 0

    # 这个方法显示实时进度，直接在前端就可以实现，因此暂时不需要这方法了
    def on_progress(self): 
        """Override this function to handle progress of receiving data."""
        if self.total:
            new_percent = self.received * 100 // self.total
            if new_percent != self.percent:
                self.percent = new_percent
                print("progress", new_percent)


class FileUploadHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('upload.html')


@stream_request_body
class FileUploadAjaxHandler(tornado.web.RequestHandler):
    def prepare(self):
        """定义一个PostDataStreamer，作为stream_request_body接收data的处理类"""
        try:
            total = int(self.request.headers.get("Content-Length", "0"))
        except:
            total = 0
        if is_print_test:
            print '[the size of data]', total
        self.ps = MyPostDataStreamer(total, tmpdir=UPLOAD_PATH)


    def data_received(self, chunk):
        """这个方法是tornado.web模块 stream_request_body 必须实现的数据接收方法"""
        self.ps.receive(chunk)

    def post(self):
        try:
            self.ps.finish_receive()
            # 必须显式调用ps的数据接收处理方法 finish_receive()
            self.set_header("Content-Type", "text/plain")
            if is_print_test:
                # print self.get_argument("username") #使用了stream_request_body之后，无法这样取值了
                print(self.ps.get_values(self.ps.get_nonfile_names()))
                print(self.ps.get_argument(u"username"))
                # 在post_streamer构造了这个名字的函数，与handler保持一致
                print(self.ps.get_argument(u"car"))

        finally:
            ps_save2db(self.ps, psdb, 'admin', is_print_test)  # user='admin' 正式使用时候，需要从页面读取文件上传者
            # 第四个参数printchunk，默认False，设置True可打印查看当前的文件流PostDataStreamer信息
            self.write("上传成功")


class FileUploadTestHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("upload test , hello world")
