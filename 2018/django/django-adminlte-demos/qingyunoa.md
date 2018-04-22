# 轻云办公套件
https://github.com/lyhapple/qingyunoa   
基于lyhapple/django-adminlte.git开源快速开发平台开发


## 准备工作：

推荐使用virutalenv环境

1. pip install virtualenv
2. virtualenv oa
3. source oa/bin/activate
4. cd oa


## 跑起来

1. git clone git@github.com:lyhapple/qingyunoa.git
2. cd qingyunoa
3. pip install -r requirement.txt
4. python manage_dev.py migrate
5. python manage_dev.py loaddata conf/fixture_data.json
6. python manage_dev.py runserver

## 使用

### 用户文档

请参考 docs/manual.md

如需fork，请使用develop分支，并向该分支提交 pull request。


### 使用

1. 超管用户名及密码都是: admin

2. django自带后台地址为: /admin/

