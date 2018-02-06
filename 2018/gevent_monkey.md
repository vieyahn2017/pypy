gevent用monkey可以直接把python的线程变成greenlet

```python 
from gevent import monkey
from flask_app import app

"""
Monkey补丁让Python线程模式支持Gevent
"""
monkey.patch_all()
#协程你可以理解为单线程无锁版线程，线程调度由你自己来。
```
