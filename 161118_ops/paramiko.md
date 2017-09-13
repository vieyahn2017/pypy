http://www.cnblogs.com/gannan/archive/2012/02/06/2339883.html



#paramiko的安装与使用

##一：简介

paramiko是用python语言写的一个模块，遵循SSH2协议，支持以加密和认证的方式，进行远程服务器的连接。

由于使用的是python这样的能够跨平台运行的语言，所以所有python支持的平台，如Linux, Solaris, BSD, MacOS X, Windows等，paramiko都可以支持，因此，如果需要使用SSH从一个平台连接到另外一个平台，进行一系列的操作时，paramiko是最佳工具之一。

举个常见的例子，现有这样的需求：需要使用windows客户端，远程连接到Linux服务器，查看上面的日志状态，大家通常使用的方法会是：

1：用telnet

2：用PUTTY

3：用WinSCP

4：用XManager等…

那现在如果需求又增加一条，要从服务器上下载文件，该怎么办？那常用的办法可能会是：

1：Linux上安装FTP并配置

2：Linux上安装Sambe并配置…

大家会发现，常见的解决方法都会需要对远程服务器必要的配置，如果远程服务器只有一两台还好说，如果有N台，还需要逐台进行配置，或者需要使用代码进行以上操作时，上面的办法就不太方便了。

使用paramiko可以很好的解决以上问题，比起前面的方法，它仅需要在本地上安装相应的软件（python以及PyCrypto），对远程服务器没有配置要求，对于连接多台服务器，进行复杂的连接操作特别有帮助。

 

##二：安装

安装paramiko有两个先决条件，python和另外一个名为PyCrypto的模块。

通常安装标准的python模块，只需要在模块的根目录下运行：

python setup.py build

python setup.py install
以上两条命令即可，paramiko和PyCrypto也不例外，唯一麻烦的就是安装PyCrypto时，需要GCC库编译，如果没有GCC库会报错，会导致PyCrypto以及paramiko无法安装。

以下以32 位的windows XP为例，说明paramiko的安装过程

 

1：安装python，2.2以上版本都可以，我使用的是2.5，安装过程略，并假设安装目录是c:\python。

 

2：判断本地是否安装了GCC，并在PATH变量可以找到，如果没有，可使用windows 版的GCC，即MinGW，下载地址：http://sourceforge.net/projects/mingw/，然后运行下载后的exe文件进行网络安装，假设目录为C:\mingw，在PATH中加入 C:\mingw\bin，并在c:\python\lib\distutils下新建一个名称是distutils.cfg的文件，填入：

[build] 
compiler=mingw32
 

3：下载PyCrypto ,地址是   

https://www.dlitz.net/software/pycrypto/

安装PyCrypto:   

解压缩   
在dos下进入解压缩的目录，运行
C:\python\python.exe setup.py build   

C:\python\python.exe setup.py install   
 

安装测试   
　　运行python.exe，在提示符下输入：   

Import  Crypto   
　　如果没有出现错误提示，说明Crypto安装成功   

 

4：下载paramiko，地址是http://www.lag.net/paramiko/   

解压缩
在dos下进 入解压缩的目录，运行   
C:\python\python.exe setup.py build   

C:\python\python.exe setup.py install   
测试paramiko
　　运行python.exe，在提示符下输入：   

Import  paramiko
　　如果没有出现错误提示，说明paramiko安装成功   

 

##三： 使用paramiko

 

如果大家感觉安装paramiko还是略有麻烦的话，当使用到paramiko提供的方便时便会觉得这是十分值得的。

下面是两种使用paramiko连接到linux服务器的代码

方式一：
```python
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("某IP地址",22,"用户名", "口令")
```
上面的第二行代码的作用是允许连接不在know_hosts文件中的主机。

 

方式二：
```python
t = paramiko.Transport((“主机”,”端口”))
t.connect(username = “用户名”, password = “口令”)
```
如果连接远程主机需要提供密钥，上面第二行代码可改成：

t.connect(username = “用户名”, password = “口令”, hostkey=”密钥”)
 

下面给出实际的例子：

###3.1 windows对linux运行任意命令,并将结果输出

如果linux服务器开放了22端口，在windows端，我们可以使用paramiko远程连接到该服务器，并执行任意命令，然后通过 print或其它方式得到该结果，

代码如下：

```python
#!/usr/bin/python 
import paramiko
 
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("某IP地址",22,"用户名", "口令")
stdin, stdout, stderr = ssh.exec_command("你的命令")
print stdout.readlines()
ssh.close()
```
其中的”你的命令”可以任意linux支持的命令，如一些常用的命令：


df：查看磁盘使用情况   
uptime：显示系统运行时间信息   
cat：显示某文件内容   
mv/cp/mkdir/rmdir:对文件或目录进行操作   
/sbin/service/ xxxservice start/stop/restart：启动、停止、重启某服务   
netstat -ntl |grep 8080：查看8080端口的使用情况    
 或者 nc -zv localhost ：查看所有端口的使用情况    
find / -name XXX：查找某文件   
...

这样一来，对于linux的任何操作几乎都可以通过windows端完成，如果对该功能进行引申，还可以同时管理多台服务器。

 

###3.2 从widnows端下载linux服务器上的文件

```python
#!/usr/bin/python 
import paramiko
 
t = paramiko.Transport((“主机”,”端口”))
t.connect(username = “用户名”, password = “口令”)
sftp = paramiko.SFTPClient.from_transport(t)
remotepath=’/var/log/system.log’
localpath=’/tmp/system.log’
sftp.get(remotepath, localpath)
t.close()
```
 

###3.3 从widnows端上传文件到linux服务器

```python
#!/usr/bin/python 
import paramiko

t = paramiko.Transport((“主机”,”端口”))
t.connect(username = “用户名”, password = “口令”)
sftp = paramiko.SFTPClient.from_transport(t)
remotepath=’/var/log/system.log’
localpath=’/tmp/system.log’
sftp.put(localpath,remotepath)
t.close()
```

我对paramiko的使用也刚刚开始，以上若有不对的地方，敬请大家指正！先谢了！