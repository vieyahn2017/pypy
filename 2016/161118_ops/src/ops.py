#coding:utf-8 
import os.path
import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.escape import json_encode
import torndb
import json
#import salt.client
import time
import shutil
from tasks import commandtask
from tasks import pushfiletask
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

status_success = {
            "status": True,
            "value":1

        }
 
status_fail = {
            "status": False,
            "value":2

        }
        
db=torndb.Connection("127.0.0.1","ops","ops","ops")

'''
认证基础类
'''
class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")

#命令任务页面渲染
class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('task.html')

#推送文件页面渲染
class PushFileWeb(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('pushfile.html')


'''
接收脚本任务的提交及处理
'''
class TaskHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = self.request.arguments 
        print "提交上来的内容"+str(data)
        #print data['shellname'][0]
        shellcontent = data['shellcontent'][0]
        shelltype = data['shelltype'][0]
        timekey= data['timekey'][0]
        if not timekey:
            self.write('no timestamp')
        #根据脚本类型定脚本后缀名称
        scriptname="run.sh"
        if shelltype=="pyhon":
            scriptname="run.py"
        file_object = open("/srv/salt/scripts/%s" % scriptname,"w")
        file_object.write(shellcontent)
        file_object.close()
        os.popen('dos2unix /srv/salt/scripts/%s' % scriptname)
        if not data.has_key('devsarr'):
            ress={"status":1,"value":"no devs"}
            self.write(json_encode(ress))
            return
        #循环设备
        for devid in data['devsarr']:
            #print i
            info = db.query('select * from host_devs where id='+devid)[0]
            print info
            ip = info['ip']
            print "ip:"+ip
            #port=info['port']
            #user = info['user']
            #passwd = info['passwd']
            commandtask.delay(timekey,ip,scriptname)
            ress={"status":0,"value":"任务已提交"}
        self.write(json_encode(ress))

'''
处理文件推送请求
'''
class PushFileHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = self.request.arguments
        print data
        timekey= data['timekey'][0]
        s_file_path=data['s_file_path'][0]
        filename=s_file_path.split('/')[-1]
        copyinfo=None
        if "salt://files/" not in s_file_path:
            print "not in salt://"
            if os.path.exists(s_file_path):
                #如果filse目录不存在则创建
                if not os.path.exists('/srv/salt/files'):
                    os.makedirs('/srv/salt/files')
                #复制源文件到salt的files目录
                shutil.copyfile(s_file_path,"/srv/salt/files/%s" %filename)
            else:
                print "no"
                copyinfo= "%s is not exist" % s_file_path
                print copyinfo
        d_file_path=data['d_file_path'][0]
        if not data['devsarr']:
            ress={"status":1,"value":"no devs!"}
            self.write(json_encode(ress))
        #循环设备
        for devid in data['devsarr']:
            info = db.query('select * from host_devs where id='+devid)[0]
            print info
            ip = info['ip']
            print "ip:"+ip
            
            pushfiletask.delay(copyinfo, timekey, ip, filename, s_file_path, d_file_path)
            ress={"status":0,"value":"提交任务成功"}
        self.write(json_encode(ress))

'''
获取设备列表设备列表页面
'''
class GetHostList(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        #self.write(json.dumps(db.query('select * from host_devs')))
        data=db.query('select * from host_devs')
        json_data=json.dumps(data)
        #print json_data
        #print type(json_data)
        self.render('hostlist.html',hosts=data)

'''
修改主机信息
'''
class SetHostHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = self.request.arguments
        id = data['id'][0]
        ip = data['ip'][0]
        desc = data['desc'][0]
        grp = data['grp'][0]
        #print id,ip,desc,grp
        print db.execute('update host_devs set dev_desc=%s,dev_grp=%s where id=%s',desc,grp,id)
        self.write(json_encode(status_success))

'''
获取设备列表--操作页
'''
class GetHostsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write(json.dumps(db.query('select * from host_devs')))

'''
查询任务的结果-key（用timestamp）+ip
'''
class GetTaskresHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = self.request.arguments
        timestamp = data['timestamp'][0]
        ip = data['ip'][0]
        print timestamp,ip
        res =db.query('select *  from task_res where keyname="'+timestamp+'" and hostdev="'+ip+'"')
        print res
        devip=res[0]['hostdev']
        rescontent=res[0]['res_content']
        status=res[0]['status']
        print "ipip:"+devip
        dev_desc = db.query("select dev_desc from host_devs where ip=%s",devip)
        dev_desc = dev_desc[0]['dev_desc']
        print "devdesc",dev_desc
        print "content:",rescontent
        ress = "%s - [%s]:\n%s\n\n"% (devip,dev_desc,rescontent.decode("utf-8"))
        print "ress:"
        data = {"status":status,"html":ress,"ip":devip}
        print "data:"
        print data
        self.write(json_encode(data))

'''
自动salt搜索新机器添加入库
'''
class AutoAddHostHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        tmp=os.popen('salt-key -l acc --out=json').read()
        tmp=json.loads(tmp)
        for ip in tmp['minions']:
            print ip
            res = db.query('select id from host_devs where ip=%s',ip)
            if not res:
                print "kong"
                tmp= os.popen("salt '%s' test.ping --out=json"%ip).read()
                tmp=json.loads(tmp)
                if tmp[ip]:
                    print db.execute("insert into host_devs (ip,status) values(%s,0)",ip)
                else:
                    print db.execute("insert into host_devs (ip) values(%s)",ip)
            else:
                print "you"
'''
登陆页
'''
class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username=self.get_argument("username")
        password=self.get_argument("password")
        if username=="admin" and password =="admin":
            self.set_secure_cookie("username", self.get_argument("username"),expires_days=None, expires=time.time()+3600)
            self.redirect("/")
        else:
            self.redirect("/login")

class LogoutHandler(BaseHandler):
    def post(self):
        #if (self.get_argument("logout", None)):
        self.clear_cookie("username")
        self.redirect("/login")

if __name__ == '__main__':
    tornado.options.parse_command_line()
    settings = {
        "cookie_secret": "bZJc2sWLDKgdkdhDO/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "xsrf_cookies": True,
        "login_url": "/login"                                    
    }
    app = tornado.web.Application(
        handlers=[(r'/', GetHostList), (r'/mytask',TaskHandler),
            (r'/gethostlist',GetHostList),
            (r'/comtask',IndexHandler),
            (r'/modify_host',SetHostHandler),
            (r'/auto_add_host',AutoAddHostHandler),
            (r'/pfiletask',PushFileWeb),(r'/pushfile',PushFileHandler),
            (r'/get_host_devs',GetHostsHandler),
            (r'/get_task_res',GetTaskresHandler),
            (r'/login',LoginHandler),
            (r'/logout', LogoutHandler)],
        cookie_secret="bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        login_url="/login",
        xsrf_cookies=True,
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
