# -*- coding: utf-8 -*- 

# http://blog.csdn.net/zhthl20091003/article/details/7699154

from twisted.internet import reactor, defer, protocol 

class CallbackAdnDisconnectProtocol(protocol.Protocol):
	def connectionMade(self):
		self.factory.deferred.callback("connected")
		# “事件响应器”handleSuccess对此事件作出处理 
		self.transport.loseConnection()

class ConnectionTestFactory(protocol.ClientFactory): 
# Twisted建立网络连接的固定套路 
	Protocol = CallbackAdnDisconnectProtocol

	def __init__(self):
		self.deferred = defer.Deferred()

	def clientConnectionFailed(self, connector, reason):
		self.deferred.errback(reason)

def testConnect(host,port):
	testFactory = ConnectionTestFactory()
	reactor.connectTCP(host, port, testFactory)
	return testFactory.deferred

def handleSuccess(result, port):
	print "connection to port %i" % port
	reactor.stop()

def handleFailure(failure, port):
	print "Error connecting to port %i: %s" %(port, failure.getErrorMessage())
	reactor.stop()

if __name__ == "__main__":
	host = "localhost"
	port = 8888
	connecting = testConnect(host, port)
	connecting.addCallback(handleSuccess, port)
	connecting.addErrback(handleFailure, port)
	reactor.run()


# 运行不成功。。。先熟悉下写法而已