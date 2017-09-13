# -*- coding:utf-8 -*-
# --------------------
# Author:		Yh
# Description:
# --------------------

from tornado.web import authenticated, stream_request_body
from modules.common.controller.base import BaseHandler

import tornado.web

from ..view.forms import UploadForm, UploadForm2
import os.path
import tempfile


class MainHandler(tornado.web.RequestHandler):
    def post(self):
        pass

    def prepare(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)

    def data_received(self, chunk):
        self.temp_file.write(chunk)

#@stream_request_body        
class FileUploadHandler(tornado.web.RequestHandler):

    def prepare(self):
        self.temp_file = '12344   ----'

    def get(self):
        form = UploadForm()
        self.render('yh/upload.html',form=form)


    def post1(self):
        upload_path=os.path.join(os.path.dirname(__file__),'files')  #文件的暂存路径
        file_metas=self.request.files['file']    #提取表单中‘name’为‘file’的文件元数据
        for meta in file_metas:
            filename=meta['filename']
            filepath=os.path.join(upload_path,filename)
            with open(filepath,'wb') as up:      #有些文件需要已二进制的形式存储，实际中可以更改
                up.write(meta['body'])
            self.write('finished!')

    @tornado.web.asynchronous
    def post(self):
        #print self.request.files

        #file_body = self.request.files['image'][0] #['body']
        #img = Image.open(StringIO.StringIO(file_body))
        #img.save("../img/", img.format)

        #f=open('D:/123.jpg', 'w')
        #f.write(  file_body  )
        #for t in file_body:f.write(t)
        #print file_body
        # form.image  -- <input id="image" name="image" type="file">


        UPLOAD_PATH ='D:/manyouthgit/upload/'
        form = UploadForm(self.request.arguments)
        print self.request.arguments

        _data = self.request.files[form.filename.name][0]

        file_name = _data['filename']
        file_type = _data['content_type']
        file_body = _data['body']
        print file_name,file_type
        f=open(os.path.join(UPLOAD_PATH, file_name), 'w')
        f.write(file_body)

        import time
        time.sleep(10)

        
        #self.write("file is uploaded ~~")
        print("file is uploaded")
        #目前还有图片不能正确显示的bug


        self.finish("file   is uploaded...    finish")


class FileUploadAjaxHandler(tornado.web.RequestHandler):
    def post(self):

        UPLOAD_PATH ='D:/manyouthgit/upload/'
        #import time
        #time.sleep(10)

        #try:
        _files=self.request.files
        print len(_files)
        #for i,f in enumerate(_files):#不能这样用,f的使用是个问题
             #_data = _files['file'+str(i)][0]       
        for i in range(len(_files)):
            _data = _files['file'+str(i)][0]

            file_name = _data['filename']
            file_type = _data['content_type']
            file_body = _data['body']
            print file_name, file_type
            print("file   %s   is uploaded"%file_name)
            tempf = tempfile.NamedTemporaryFile(dir=UPLOAD_PATH, delete=False)
            tempf.write(file_body)
            print tempf.name

            #fs=open(os.path.join(UPLOAD_PATH, file_name), 'w')
            #fs.write(file_body)

        #except Exception,e:
            #print "Error: %s" % e
        self.write("上传成功")

    #def get(self):
        #self.write("get hello world")



class FileUploadBlockTestHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("get hello world")