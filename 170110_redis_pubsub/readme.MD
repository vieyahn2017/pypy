#Redis学习笔记8--Redis发布订阅

运行此java程序 JRedisCli  

启动redis-cli 订阅  
redis 127.0.0.1:6379> psubscribe news.*  

再启动一个redis-cli用来发布两条消息：  
redis 127.0.0.1:6379> publish news.share "share a link http://www.google.com"  
(integer) 2  
redis 127.0.0.1:6379> publish news.blog "I post a blog"  
(integer) 2  


【python的接收端未完成pubsub_news.py】