# -*- coding:utf-8 -*-
#!/usr/bin/env python
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url, stream_request_body
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from post_streamer import PostDataStreamer
import sys


import tornpg
POSTGRES_HOST = "localhost"
POSTGRES_USER = "lcic"
POSTGRES_DB   = "lcic_db"
POSTGRES_PWD  = "123456"

psdb = tornpg.Connection(
            host = POSTGRES_HOST,database = POSTGRES_DB,
            user = POSTGRES_USER,password = POSTGRES_PWD)

#from modules.common.model.dbManager import psdb
#app.py这个路径往下找，我这不是handler所以无法导入

class MyPostDataStreamer(PostDataStreamer):
    percent = 0

    def on_progress(self):
        """Override this function to handle progress of receiving data."""
        if self.total:
            new_percent = self.received*100//self.total
            if new_percent != self.percent:
                self.percent = new_percent
                print("progress",new_percent)

@stream_request_body 
class StreamHandler(RequestHandler):
    def get(self):
        self.write('''<html><body>
                        <form method="POST" action="/" enctype="multipart/form-data">
                        File #1: <input name="file1" type="file"><br>
                        File #2: <input name="file2" type="file"><br>
                        File #3: <input name="file3" type="file"><br>
                        Other field 1: <input name="other1" type="text"><br>
                        Other field 2: <input name="other2" type="text"><br>
                        <input type="submit">
                        </form>
                        </body></html>''')

    def post2(self):
        self.ps.finish_receive()
        self.set_header("Content-Type","text/plain")
        self.ps.examine()
        #self.ps.release_parts()

    def post(self):
        #这段代码把标准输出到request的write ,最后输出完毕又换回来
        try:
            #self.fout.close()
            self.ps.finish_receive()
            # Use parts here!
            self.set_header("Content-Type","text/plain")
            oout = sys.stdout
            try:
                sys.stdout = self
                self.ps.examine()
            finally:
                sys.stdout = oout
        finally:
            # Don't forget to release temporary files.
            #self.ps.release_parts()
            self.ps.save_parts(psdb)


    def prepare(self):
        # TODO: get content length here?
        try:
            total = int(self.request.headers.get("Content-Length","0"))
        except:
            total = 0
        self.ps = MyPostDataStreamer(total,tmpdir="D:/manyouthgit/upload") #,tmpdir="/tmp"
        #self.fout = open("raw_received.dat","wb+")

    def data_received(self, chunk):
        #self.fout.write(chunk)
        self.ps.receive(chunk)

def main():
    application = Application([
        url(r"/", StreamHandler),
    ],
    debug= True)
    max_buffer_size = 4 * 1024**3 # 4GB
    http_server = HTTPServer(
        application,
        max_buffer_size=max_buffer_size,
    )
    http_server.listen(8888)
    IOLoop.instance().start()

main()