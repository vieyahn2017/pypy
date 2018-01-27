# -*- coding: utf-8 -*- 

from twisted.internet import reactor,protocol

class QuickClient(protocol.Protocol): 
	def connectionMade(self): 
		print dir(self.transport.getPeer()) 
		print [item for item in dir(self.transport.getPeer()) if not item.startswith('_')]
		print filter(lambda i: not i.startswith('_'), dir(self.transport.getPeer()))
		print "port:%s type:%s "%(self.transport.getPeer().port, self.transport.getPeer().type)
		print "connection to ",self.transport.getPeer().host

class BasicClientFactory(protocol.ClientFactory):
	protocol = QuickClient
	def clientConnectionLost(self, connector, reason): 
		print "connection lost ",reason.getErrorMessage()
		reactor.stop()

	def clientConnectionFailed(self, connector, reason):
		print "connection failed ",reason.getErrorMessage()
		reactor.stop() 

reactor.connectTCP('127.0.0.1', 8080, BasicClientFactory())
reactor.run()

# connectionMade：链接成功后自动调用
# Factory的作用是管理连接事件
# clientConnectionLost：连接断开或丢失时调用
# clientConnectionFailed：连接失败时调用
# transport为Protocol一个内建属性 getPeer 对象包含有连接信息（域名、端口、类型(TCP,UDP)）