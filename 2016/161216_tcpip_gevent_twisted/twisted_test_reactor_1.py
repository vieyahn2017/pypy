# -*- coding: utf-8 -*- 

from twisted.internet import reactor
import time

def printTime():
	print "Current time is", time.strftime("%H:%M:%S") 

def stopReactor( ): 
	print "Stopping reactor" 
	reactor.stop( ) 	

reactor.callLater(1, printTime) 
#定时器，1秒钟后调用printTime() 

reactor.callLater(2, printTime) 

reactor.callLater(3, printTime) 

reactor.callLater(5, stopReactor) 
#定时器，5秒钟后调用stopReactor() 

print "Running the reactor..." 

reactor.run( ) 

print "Reactor stopped." 