# -*- coding: utf-8 -*-

import urllib2
import re
import urllib

url="http://fanyi.baidu.com/"
searchword="how deep i love you"

values = {"query":searchword,}
data = urllib.urlencode(values)
request = urllib2.Request(url,data)
response = urllib2.urlopen(request)
#print response.read()

from lxml import etree;
z=etree.HTML(response.read()).xpath('//div[@class="translate-wrap"]')[0]
print z


