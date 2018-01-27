# Python的logging


```python
def compositeLogger(name, level, log_file):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

```



# 3.将日志同时输出到文件和屏幕
```python
import logging

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='myapp.log',
    filemode='w')

#################################################################################################
# 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
#################################################################################################

logging.debug('This is debug message')
logging.info('This is info message')
logging.warning('This is warning message')
```
屏幕上打印:
```bash
root        : INFO     This is info message
root        : WARNING  This is warning message
./myapp.log文件中内容为:
Sun, 24 May 2009 21:48:54 demo2.py[line:11] DEBUG This is debug message
Sun, 24 May 2009 21:48:54 demo2.py[line:12] INFO This is info message
Sun, 24 May 2009 21:48:54 demo2.py[line:13] WARNING This is warning message
```


## Logger.setLevel(lvl)
设置logger的level， level有以下几个级别：   
　　　　
　　级别高低顺序：NOTSET < DEBUG < INFO < WARNING < ERROR < CRITICAL   
如果把looger的级别设置为INFO， 那么小于INFO级别的日志都不输出， 大于等于INFO级别的日志都输出　 　

代码如下:
```python
logger.debug("foobar")    # 不输出   
logger.info("foobar")        # 输出  
logger.warning("foobar")  # 输出  
logger.error("foobar")      # 输出  
logger.critical("foobar")    # 输出  

```

Logger.addHandler(hdlr)   
通过handler对象可以把日志内容写到不同的地方。比如简单的StreamHandler就是把日志写到类似文件的地方。python提供了十几种实用handler，比较常用有：   
```python
StreamHandler: 输出到控制台
FileHandler:   输出到文件
BaseRotatingHandler 可以按时间写入到不同的日志中。比如将日志按天写入不同的日期结尾的文件文件。
SocketHandler 用TCP网络连接写LOG
DatagramHandler 用UDP网络连接写LOG
SMTPHandler 把LOG写成EMAIL邮寄出去
```

format: 指定输出的格式和内容，format可以输出很多有用信息，如上例所示:
```bash
 %(levelno)s: 打印日志级别的数值
 %(levelname)s: 打印日志级别名称
 %(pathname)s: 打印当前执行程序的路径，其实就是sys.argv[0]
 %(filename)s: 打印当前执行程序名
 %(funcName)s: 打印日志的当前函数
 %(lineno)d: 打印日志的当前行号
 %(asctime)s: 打印日志的时间
 %(thread)d: 打印线程ID
 %(threadName)s: 打印线程名称
 %(process)d: 打印进程ID
 %(message)s: 打印日志信息
datefmt: 指定时间格式，同time.strftime()
level: 设置日志级别，默认为logging.WARNING
stream: 指定将日志的输出流，可以指定输出到sys.stderr,sys.stdout或者文件，默认输出到sys.stderr，当stream和filename同时指定时，stream被忽略
```
