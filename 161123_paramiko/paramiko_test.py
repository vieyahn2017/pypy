# -*- coding: utf-8 -*- 
#!/usr/bin/python
import paramiko

# paramiko连接到linux服务器的代码 
# 方式一：
# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ss.connect("某IP地址", 22, "用户名", "口令")
# 方式二：
# t = Transport(("主机", "端口"))
# t.connect(username = "用户名", password = "口令") #  hostkey="密钥"


# 3.1 windows对linux运行任意命令,并将结果输出
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ss.connect("某IP地址", 22, "用户名", "口令")
stdin, stdout, stderr = ssh.exec_command('ifconfig;free;df -h;ls') # "你的命令"
print stdout.readlines()
ss.close()

"""
其中的"你的命令"可以任意linux支持的命令，如一些常用的命令：
df：查看磁盘使用情况
uptime：显示系统运行时间信息
cat：显示某文件内容
mv/cp/mkdir/rmdir:对文件或目录进行操作
/sbin/service/ xxxservice start/stop/restart：启动、停止、重启某服务
netstat -ntl |grep 8080：查看8080端口的使用情况 
 或者 nc -zv localhost ：查看所有端口的使用情况 
find / -name XXX：查找某文件
"""

# 3.2 从widnows端下载linux服务器上的文件
t = paramiko.Transport(("主机", "端口"))
t.connect(username = "用户名", password = "口令") #  hostkey="密钥"
sftp = paramiko.SFTPClient.from_transport(t)
remotepath = '/var/log/system.log'
localpath = '/tmp/system.log'
sftp.get(remotepath, localpath)
t.close()

# 3.3 从widnows端上传文件到linux服务器
t = paramiko.Transport(("主机", "端口"))
t.connect(username = "用户名", password = "口令") #  hostkey="密钥"
sftp = paramiko.SFTPClient.from_transport(t)
remotepath = '/var/log/system.log'
localpath = '/tmp/system.log'
sftp.putt(localpath, remotepath)
t.close()



# 利用配置文件登录批量主机 
# config.ini配置文件内容：
# [IP]
# ipaddress = 74.63.229.*;69.50.220.*


#!/usr/bin/env python    
import paramiko    
import os    
import datetime    
from ConfigParser import ConfigParser    
configFile = 'config.ini'
config = ConfigParser()    
config.read(configFile)    
hostname1 = ''.join(config.get('IP','ipaddress'))    
address=hostname1.split(';')    
print address    
username = 'root'
password = 'abc123'
port = 22
local_dir = '/tmp/'
remote_dir = '/tmp/test/'
if __name__=="__main__":    
    for ip in address:    
        paramiko.util.log_to_file('paramiko.log')    
        s = paramiko.SSHClient()    
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())    
        s.connect(hostname=ip, username=username, password=password)    
        stdin,stdout,stderr = s.exec_command('free;ifconfig;df -h')    
        print stdout.read()    
        s.close()