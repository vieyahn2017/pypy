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


def read_remote_file_D(upload_file_D, is_log=True):
    """ 远程读文件， 返回lines  这个方法只用于处理D文件"""
    ouput_lines = [] #用文本数组，最后用|合并
    for line in upload_file_D:
        if line.startswith('TX'):
            # 详细条目
            ouput_lines.append('TX') # append content
    return ouput_lines
    
def write_file_with_lines(filename, lines_list):
    # 把lines_list写入文件filename
    for line in lines_list:
        filename.write(line)
        filename.write('\n')
        
sftp_client = get_remote_sftp_client(hostname=config.file_interfaceHost, 
                                     port=config.file_interfacePort, 
                                     username=config.file_userName, 
                                     password=config.file_pwd)

remote_path = "/opt/file/fund-gw/share-dir/export/settle/fundout/generate/"

the_day = '20180108' # 每次手动改这里吧

def main(sftp_client, remote_path_add_the_day):
    """ the main function """

    # 这两种写法都可以
    # sftp_client.chdir(remote_path_add_the_day)
    # the_day_remote_dirs = sftp_client.listdir()
    the_day_remote_dirs = sftp_client.listdir(remote_path_add_the_day)

    dirs_dicts = {}
    # 列出该目录下所有gbk文件，并生成一个以序号为主键的dict
    for no, one_file in enumerate(the_day_remote_dirs):
        if one_file.endswith('gbk.txt'):
            print no, one_file
            dirs_dicts[str(no)] = one_file

    print "please choose your file: "
    file_no = raw_input()
    one_file = dirs_dicts[file_no]
    upload_file = sftp_client.open(remote_path_add_the_day + '/' + one_file, 'r')

    all_lines = []
    # 按 ODE文件的不同，选择不同的执行方法
    if 'D' in one_file:
        all_lines = read_remote_file_D(upload_file)
    else:
        print "can not recognize your file."
    
    download_file = sftp_client.open(remote_path_add_the_day + '/' + one_file.replace('gbk', 'back'), 'w')
    write_file_with_lines(download_file, all_lines)


main(sftp_client, remote_path + the_day)
