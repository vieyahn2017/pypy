import urllib
import re

regex='http\:\/\/[^<>\"]*\.js'
url="http://www.baidu.com"

bd=urllib.urlopen(url)
ts=re.findall(regex, bd.read())
#print ts
for t in ts: print t

print bd.info()
print bd.getcode()

