利用saltstack的salt.client模块可以在python的命令行下或者python脚本里执行相应的salt命令   

master端想要执行类似 salt '*' cmd.run 'uptime' 在saltclient里可以这么写   
```python
import salt.client 

local = salt.client.LocalClient() 
local.cmd('*', 'cmd.run', ['uptime'])
```

也可以放到后台执行只返回一个jid
```python
cmd_async('*', 'cmd.run', ['uptime'])
```

得到jid可以通过get_cache_returns(jid)方法来获取执行结果，在没有执行完成以前是为空的所以可以写一个while来一直读取结果直到读取到或者超出规定时间为止
```python
import salt.client
local = salt.client.LocalClient()
t = 0
jid = local.cmd_async('*', 'cmd.run', ['uptime'])
while not local.get_cache_returns(jid):
    time.sleep(1)
    if t == 8:
        print 'Connection Failed!'
        break
    else:
        t+=1
print local.get_cache_returns(jid)
```

minion端可以用来直接在minions上执行命令或者也可以用来写returnner的时候获取minion的grain信息等
```python
import salt.client 
caller = salt.client.Caller() 
caller.sminion.functions['cmd.run']('ls -l')
```

获取grains的信息
```python
import salt.client
caller = salt.client.Caller()
caller.sminion.functions['grains.items']  #grains.items代表获取全部的grains信息
caller.sminion.functions['grains.item']('os') #想要特定的grains信息用grains.item然后在后面指定
```

本文出自 “日光倾城” 博客，，请务必保留此出处