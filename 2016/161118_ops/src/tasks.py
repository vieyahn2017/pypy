# tasks.py
#coding:utf-8 
import time
import torndb
import json
import salt.client
from celery import Celery,platforms

app = Celery('tasks', broker='redis://:kdredis1@localhost:6001/0')
platforms.C_FORCE_ROOT = True
# 因为supervisord默认是用root运行的，必须设置以下参数为True才能允许celery用root运行

db=torndb.Connection("127.0.0.1","ops","ops","ops")

#salt执行的方法
def saltdoshell(ip,scriptname):
    try:
        client = salt.client.LocalClient()
        res = client.cmd(ip,'cmd.script',['salt://scripts/%s' % scriptname],timeout=5)
        return res
    except:
        return None

@app.task(name="tasks.commandtask")
def commandtask(timekey, ip, scriptname , max_retries=3):
    STATUS=1
    #调用salt函数执行脚本
    res = saltdoshell(ip,scriptname)
    print res
    if not res:
        #time.sleep(5)
        res = saltdoshell(ip,scriptname)
        if not res:
            #time.sleep(10)
            res = saltdoshell(ip,scriptname)
    if res:
        stderr = res[ip]['stderr']
        stdout = res[ip]['stdout']
        if stderr:
            allres = stderr+'\n'+stdout
        else:
            allres = stdout
    else:
        allres = "执行失败"
        STATUS=0
    print "allres:"+allres
    #下面这句解决内容有 单双引引起的问题
    allres=allres.replace("'","\\'").replace('"','\\"')
    print allres
    #获取脚本执行结果回写mysql
    
    exe="insert into task_res(keyname,hostdev,status,res_content ) values('%s','%s',%d,'%s')" % (timekey,ip,int(STATUS),allres.decode("utf-8"))
    #exe="insert into task_res(keyname,hostdev,res_content ) values('%s','%s',\"%s\")" % (timekey,ip,data)
    dbres=db.execute(exe)
    print type(dbres)
    print dbres
    
@app.task(name="tasks.pushfiletask")
def pushfiletask(copyinfo, timekey, ip, filename, s_file_path, d_file_path):
    STATUS=1
    #调用salt api执行推送任务
    client = salt.client.LocalClient()
    res = client.cmd(ip,'cp.get_file',['salt://files/%s' % filename,d_file_path])
    print res
    if res.has_key(ip):
        allres="push file Ok"
    else:
        STATUS=0
        if copyinfo:
            allres="Push file failed: %s" % copyinfo
        else:
            allres="Push file failed: %s" % s_file_path
    print "allres:"+allres
    #获取脚本执行结果回写mysql
    exe="insert into task_res(keyname,hostdev,status,res_content ) values('%s','%s',%d,'%s')" % (timekey,ip,STATUS,allres.decode("utf-8"))
    print db.execute(exe)
