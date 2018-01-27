#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import config
import paramiko

def get_remote_sftp_client(hostname, port, username, password)
    #服务器信息，主机名（IP地址）、端口号、用户名及密码
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port, username, password, compress=True)
    sftp_client = client.open_sftp()
    return sftp_client

sftp_client = get_remote_sftp_client(hostname=config.file_interfaceHost, 
                                     port=config.file_interfacePort, 
                                     username=config.file_userName, 
                                     password=config.file_pwd)

remote_path = "/opt/file/fund-gw/share-dir/export/settle/fundout/generate/"

the_day = '20180108' # 每次手动改这里吧


print("1============\n")
the_day_remote_dirs = sftp_client.listdir(remote_path + the_day)
for one_file in the_day_remote_dirs:
    print one_file
 

print("2============\n")
sftp_client.chdir(remote_path + the_day)
the_day_remote_dirs = sftp_client.listdir()
for one_file in the_day_remote_dirs:
    print one_file


print("3===========\n")
the_day_remote_dirs = sftp_client.listdir(remote_path + the_day + '/')
for one_file in the_day_remote_dirs:
    print one_file
