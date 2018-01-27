#!/usr/bin/env python
# encoding: utf-8

import urllib2
import gzip
import tornado.gen
import tornado.httpclient

from weibo_login import login

def urllib2_type(url):
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36'}
    request = urllib2.Request(url=url, headers=headers)
    response = urllib2.urlopen(request)

    print 'urllib2 get: %s' % response.url


def tornado_type(url):
    http_header   = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36'}
    http_request  = tornado.httpclient.HTTPRequest(url=url,method='GET',headers=http_header,\
                        use_gzip=True, connect_timeout=200, request_timeout=600)
    http_client   = tornado.httpclient.HTTPClient()
    http_response = http_client.fetch(http_request)

    print 'tornado httpclient get: %s' % http_response.effective_url

if __name__ == '__main__':
    username = ''
    pwd = ''
    cookie_file = 'weibo_login_cookies.dat'

    url = 'http://weibo.com/zhaodong1982'

    if login(username, pwd, cookie_file):
        print 'Login WEIBO succeeded'
        urllib2_type(url)
        tornado_type(url)


用了网上的 python 非API方式 模拟登录新浪微薄 的代码，登录成功后抓取 微薄个人页面信息。
同样的一个微薄页面，用urllib2的方式抓取一点问题都没，
如果用tornado.httpclient.HTTPClient().fetch(url)的方式抓取就会跳转到登录界面，而且始终登录不成功，何解？
注：如果是urllib2方式的话所有页面都抓取成功；tornado httpclient的方式只是部分页面会跳转到登录地址，还是有些页面可以成功抓取的。



运行结果如下，httpclient的方式地址被重定向到注册界面了：
(venv)➜ test git:(mongoengine) ✗ python test.py
Loading cookies success
Login WEIBO succeeded
urllib2 get: http://weibo.com/zhaodong1982
tornado httpclient get: http://weibo.com/signup/signup.php?inviteCode=1658066713





你使用 tornado.httpclient 时没有带 cookie。你的登录模块会使用 urllib2.install_opener 安装一个带 cookie 支持的 urlopener 到 urllib2。
但是 Tornado 的 HTTP 客户端是自己实现的，与 urllib2 没有关系。

希望 tornado.httpclient 自动帮你管理 cookie 的话，可以使用 curl 的版本 tornado.curl_httpclient.CurlAsyncHTTPClient。
具体用法请见 Tornado 及 libcurl 文档。
如果不想安装 pycurl 而使用默认的版本的话，请自行处理 Set-Cookie 和 Cookie 头，
像这样： https://github.com/lilydjwg/winterpy/blob/master/pylib/mytornado/fetchtitle.py#L453
另外，你用 tornado.httpclient.AsyncHTTPClient 才是异步的哦。