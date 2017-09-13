# -*- coding: utf-8 -*-

import urllib2
import re
import urllib
from lxml import etree;

url2="https://passport.csdn.net/account/login?from=http://my.csdn.net/my/mycsdn"
request = urllib2.Request(url2)
response = urllib2.urlopen(request)
lt_value= etree.HTML(response.read()).xpath('//input[@name="lt"]/@value')[0].strip()
print lt_value
#LT-386180-bnW0rgCg5xqHjKn9bM3gr51ZwSjeY5
#这样重新发请求是不行的
"""
 <!-- 该参数可以理解成每个需要登录的用户都有一个流水号。只有有了webflow发放的有效的流水号，用户才可以说明是已经进入了webflow流程。否则，没有流水号的情况下，webflow会认为用户还没有进入webflow流程，从而会重新进入一次webflow流程，从而会重新出现登录界面。 -->
 """
values = {}
values['username'] = "vieyahn@163.com"
values['password'] = "222959cs"
values['lt']=lt_value
#values = {"username":"1016903103@qq.com","password":"XXXX"}
data = urllib.urlencode(values)

request = urllib2.Request(url2,data)
response = urllib2.urlopen(request)
print response.read()

