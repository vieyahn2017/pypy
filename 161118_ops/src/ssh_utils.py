#!/usr/bin/env python
#coding=utf-8
'''
Created on 2015年10月21日
@author: 纸鸢
'''
import paramiko, getpass,sys,traceback

'''
一个运维工具类Myssh
login_by_passwd() -- 账号密码登陆的方式
login_by_key()    -- Key登陆方式
ssh()             -- ssh执行远程命令
scp()             -- 远程传输文件
'''
class ssh_utils():
    def login_by_passwd(self, ip, port, username, passwd):
        self.ip = ip
        self.port = port
        self.username = username
        self.passwd = passwd
        self.pkey = None
    
    def login_by_key(self, username, key_path, passwd):
        try:
            self.pkey=paramiko.RSAKey.from_private_key_file(key_path)
        except paramiko.PasswordRequiredException:
            if not passwd:
                passwd = getpass.getpass('RSA key password: ')
            self.pkey = paramiko.RSAKey.from_private_key_file(key_path, passwd) 
         
    def ssh(self,shell):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.pkey:
                ssh.connect(self.ip, self.port, self.username, compress = True, pkey= self.pkey)
            else:
                if not self.passwd:
                    self.passwd = getpass.getpass('input password: ')
                ssh.connect(self.ip,self.port,self.username, self.passwd)
            stdin, stdout, stderr = ssh.exec_command(shell)
            res = stdout.readlines()
            ssh.close()
            return res
        except:
            type, value, tb = sys.exc_info()
            return traceback.format_exception(type, value, tb)
        
    def scp(self,localpath,remotepath):
        try:
            t = paramiko.Transport((self.ip,self.port))
            if self.pkey:
                t.connect(self.ip, self.port, self.username, pkey= self.pkey)
            else:
                if not self.passwd:
                    self.passwd = getpass.getpass('input password: ')
                t.connect(username = self.username, password = self.passwd)
            sftp = paramiko.SFTPClient.from_transport(t)
            sftp.put(localpath,remotepath)
            t.close()
            return "SCP OK"
        except:
            type, value, tb = sys.exc_info()
            return traceback.format_exception(type, value, tb)

if __name__ == '__main__':
    #使用例子
    myssh = ssh_utils()
    myssh.login_by_passwd("ip",22,"username","passwd")
    myssh.scp('installtmp.tar.gz', '/tmp/installtmp.tar.gz')
    myssh.ssh("cd /tmp/ && tar xf installtmp.tar.gz && cd installtmp && sh install.sh")