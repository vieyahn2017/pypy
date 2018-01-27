# ops
简单的运维管理后台，python2.7 - tornado3 - saltstack - celery
![image3](https://github.com/cnkedao/ops/raw/master/1/3.jpg)
#依赖
基于python2.7    
基于tornado    
基于bootstrap的AdminX界面模板    
基于`saltstack`      
使用了celery，需要安装    
使用了redis，需要安装    
使用了mysql，需要安装，需要建库建表

# 功能说明
主要实现了
* 命令下发执行
* 文件下发

# 申明
本代码仅为运维开发测试代码，功能并不强大，算是一个demo，仅作为参考，不作为一个完善的项目产品。

#安装
###安装python2.7
```
yum install -y zlib-devel
wget --no-check-certificate https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tar.xz
tar xf Python-2.7.9.tar.xz
cd Python-2.7.9
./configure --prefix=/usr/local --with-zlib
make && make altinstall
```
###安装pip
```
wget https://pypi.python.org/packages/source/s/setuptools/setuptools-18.7.1.tar.gz#md5=a0984da9cd8d7b582e1fd7de67dfdbcc  --no-check-certificate
tar xvf setuptools-18.7.1.tar.gz
cd setuptools-18.7.1
python2.7 setup.py install

rm -rf pip-7.1.0.tar.gz
wget http://demo.acache.cn/pip-7.1.0.tar.gz
tar xvf pip-7.1.0.tar.gz
cd pip-7.1.0
python2.7 setup.py install
```

###安装redis
```
wget http://download.redis.io/releases/redis-3.0.6.tar.gz
tar zxf redis-3.0.6.tar.gz
cd redis-3.0.6
make
make PREFIX=/usr/local/redis install
mkdir -p /usr/local/redis/bin
mkdir -p /usr/local/redis/etc
mkdir -p /usr/local/redis/var
mkdir -p /data/redis-data/redis6001
cp redis.conf /usr/local/redis/etc/redis.conf.default
cd src
cd /usr/local/redis/etc/
cat >> /usr/local/redis/etc/redis6001.conf <<'EOF'
daemonize yes
pidfile /var/run/redis6001.pid
port 6001
loglevel notice
logfile /data/logs/redis6001.log
databases 16
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename redis6001.rdb
dir /data/redis-data/redis6001
slave-serve-stale-data yes
slave-read-only yes
slave-priority 100
appendonly no
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
lua-time-limit 5000
slowlog-log-slower-than 10000
slowlog-max-len 128
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-entries 512
list-max-ziplist-value 64
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit slave 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
requirepass kdredis1
EOF
echo "ok"
```

####启动redis
```
mkdir -p /data/logs/
/usr/local/redis/bin/redis-server /usr/local/redis/etc/redis6001.conf
```

###安装celery
```
pip2.7 install celery
pip2.7 install torndb
pip2.7 install mysql
pip2.7 install redis
```

###mysql建库建表
```
create database ops default character set utf8;
grant all privileges on ops.* to ops@'localhost' identified by'ops';

use ops

create table task(
   task_id INT NOT NULL AUTO_INCREMENT,
   shell_name VARCHAR(256) NOT NULL,
   do_user VARCHAR(20) NOT NULL,
   dst_hosts VARCHAR(2048) NOT NULL,
   shell_from VARCHAR(20) NOT NULL,
   shell_content VARCHAR(5096) NOT NULL,
   PRIMARY KEY ( task_id )
);

create table task_res(
   id INT NOT NULL AUTO_INCREMENT,
   keyname VARCHAR(512) NOT NULL,
   hostdev VARCHAR(2048) NOT NULL,
   status int(1) NOT NULL,
   res_content MEDIUMBLOB NOT NULL,
   PRIMARY KEY ( id )
);

create table host_devs(
   id INT NOT NULL AUTO_INCREMENT,
   ip VARCHAR(256) NOT NULL,
   dev_desc VARCHAR(256) NOT NULL DEFAULT 'default',
   status int(4) NOT NULL DEFAULT '2',
   dev_grp VARCHAR(256) NOT NULL DEFAULT 'default',
   PRIMARY KEY ( id )
);

```

###启动celery
在上面的准备都就绪后
在src目录下，跟tasks.py文件同级执行
```
celery -A tasks worker -c 10 --loglevel=info
```
上面是调试模式，可以看到报错信息
跑到后台模式
```
nohup celery -A tasks worker -c 10 --loglevel=info &
```
###安装saltstack服务端
```
rpm -ivh http://mirrors.sohu.com/fedora-epel/6/x86_64/epel-release-6-8.noarch.rpm
yum  -y install salt-master

cat>/etc/salt/master<<EOF
publish_port: 11438     
user: root                     
worker_threads: 1               
ret_port: 11439                
keep_jobs: 48                  
timeout: 60                     
auto_accept: False
EOF
```

###防火墙放行端口
有防火墙的话需要放行端口
```
-A RH-Firewall-1-INPUT  -p tcp -m state --state NEW -m tcp --dport 11438:11439 -j ACCEPT
```

###saltstack客户端安装举例
```
yum  -y install salt-minion
cat >/etc/salt/minion<<EOF
master: 192.168.246.128   #服务端的ip，需要修改    
id: C1-192.168.246.129     #本机的ID，需要修改，唯一     
master_port: 11439         
EOF
```

##启动ops.py
```
python2.7 ops.py
```
会监听8000端口，可以自行修改。

##登陆账号
admin/admin

##扫描节点机器到后台
在saltstack端添加到服务端之后，需要在后台web端扫描入库到mysql。
功能见首页的 “Tools”--“扫描新机器”。

##使用
上面都走通之后，就可以使用做管理了。

#工作流程

基于saltstack扫描机器存mysql——添加任务（命令/文件）——把任务丢到celery——celery用redis做队列存储——celery的tasks.py里面实现做任务action——tasks.py把任务做完反馈到mysql——前端到mysql取这次任务的结果做展示

#界面
![image1](https://github.com/cnkedao/ops/raw/master/1/1.jpg)
![image2](https://github.com/cnkedao/ops/raw/master/1/2.jpg)
![image3](https://github.com/cnkedao/ops/raw/master/1/3.jpg)
![image4](https://github.com/cnkedao/ops/raw/master/1/4.jpg)