from tornado import ioloop
from tornado.httpclient import AsyncHTTPClient

urls = ['http://www.baidu.com', 'http://www.sina.com', 'http://www.python.org']

def print_head(response):
    print ('%s: %s bytes: %r' % (response.request.url,
                                 len(response.body),
                                 response.body[:50]))

http_client = AsyncHTTPClient()
for url in urls:
    print ('Starting %s' % url)
    http_client.fetch(url, print_head)
ioloop.IOLoop.instance().start()