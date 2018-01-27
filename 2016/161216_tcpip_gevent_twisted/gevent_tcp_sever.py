# -*- coding: utf-8 -*- 

from gevent.server import StreamServer

def handle(sock, address):
    sock.recv(1000)
    sock.send("HTTP/1.1 200 OK\r\n\r\nfafdsa")

server = StreamServer(('', 8000), handle);
server.serve_forever();

# 如何来开发基于TCP的server，因为gevent自带了streamserver，其实gevent的WSGI的server也是基于streamserver来开发的。。。
# 非常的简单，只需要提供一个handle就好了。。。
# 每当listener收到了一个socket，它都将会创建一个协程，然后调用handle来处理。。所以只需要同步的方式来写代码就好了