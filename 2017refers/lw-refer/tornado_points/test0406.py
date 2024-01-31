# -*- coding:utf-8 -*- 
import  tornado.ioloop as ioloop
import  tornado.httpclient as httpclient
import  time
start = time.time()
step =  3 ;
def  handle_request(response):
     global  step
     if  response.error:
         print   "Error:" , response.error
     else :
         print  response.body
     step -=  1
     if   not  step:
        finish()
def  finish():
     global  start
     end = time.time()
     print   "一共用了 Used %0.2f secend(s)"  % float(end - start)
     ioloop.IOLoop.instance().stop()
http_client = httpclient.AsyncHTTPClient()
#这三个是异步执行的，大家可以多试试几个url，或者自己写个接口
http_client.fetch( "http://www.baidu.com" , handle_request)
http_client.fetch( "http://www.baidu.com" , handle_request)
http_client.fetch( "http://www.baidu.com" , handle_request)
ioloop.IOLoop.instance().start()