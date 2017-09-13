import urllib2
import re

regex='http\:\/\/[^<>\"]*\.js'
url="http://www.baidu.com"

bd=urllib2.urlopen(url)
print bd
"""
<addinfourl at 54448328L whose fp = <socket._fileobject object at 0x00000000033061B0>>
"""
ts=re.findall(regex, bd.read())
for t in ts: print t



request = urllib2.Request(url)
response = urllib2.urlopen(request)
print request
print response
"""
<urllib2.Request instance at 0x00000000032031C8>
<addinfourl at 54449800L whose fp = <socket._fileobject object at 0x00000000033CF390>>
"""
t2s=re.findall(regex, response.read())
for t in t2s: print t
