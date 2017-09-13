#!/usr/bin/env python
# coding=utf-8
import subprocess

# def getDom(url):
# 	cmd = 'phantomjs  contentdom.js  "%s"' %url
# 	print "cmd: " ,cmd
# 	stdout,stderr = subprocess.Popen(cmd,
# 			shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
# 		.communicate()
# 	print stderr
# 	return stdout

# 前一段时间公司需要爬取部分web页面的数据使用。但是页面中的主要数据是ajax load出来的，传统的抓取方法是拿不到数据的。
# 后来在网上发现了phantomjs，在无界面的情况下运行js，渲染dom。用这个工具抓取ajax load出来的数据再方便不过啦。
# 系统环境：CentOS release 6.5 (Final)
# phantomjs版本：1.9.8
# phantomjs抓取加载完整的dom结构。说到phantomjs怎么把数据传递给处理程序，我看到网上很多人是写一个本地文件，
# 然后具体的处理程序再读取那个文件进行处理。感觉这种方式太麻烦了，干脆将数据打印到到标准输出中，然后处理程序从标准输出中读取数据。
# 用python获取数据。然后就开始处理了。具体的处理逻辑就不展示了。

def getDom2():
	cmd = 'dir' #'phantomjs 0428-3.js'
	print "cmd: " ,cmd
	stdout,stderr = subprocess.Popen(cmd,shell=True,
		stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
	print stderr
	print stdout
	return stdout
from redis import Redis
r = Redis(host='localhost', port=6379, db=0)
r.set('key_phantom_test', getDom2())
print r.get('key_phantom_test')