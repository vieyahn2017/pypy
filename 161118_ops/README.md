#tornado写的运维管理后台

from celery import Celery,platforms   
celery做了测试   
celery有个图形化管控台flower （也是tornado写的）   

````python
import paramiko, getpass,sys,traceback
```
paramiko是用python语言写的一个模块,遵循SSH2协议,支持以加密和认证的方式,进行远程服务器的连接。 

Python 标准库 -> Getpass 模块 -> 命令行下输入密码的方法. (2012-02-03 12:04:11)转载▼   
getpass 模块提供了平台无关的在命令行下输入密码的方法.   
getpass(prompt) 会显示提示字符串, 关闭键盘的屏幕反馈, 然后读取密码.   
如果提示参数省略, 那么它将打印出 "Password:".   
getuser() 获得当前用户名, 如果可能的话.   


import salt.client   

import itertools   
迭代器