# -*- coding: utf-8 -*- 

# gevent中带有WSGI的server实现。。。
# 所以，可以很方便的利用gevent来开发http服务器。。。
# 例如如下代码，采用gevent加tornado的方式。。。。
#（tornado其实自带的有I/O循环，但是用gevent可以提高其性能。。）

from gevent import monkey;
monkey.patch_all()

from gevent.wsgi import WSGIServer
import gevent
import tornado
import tornado.web
import tornado.wsgi
import os.path
import time
import datetime
import re
import sys
import json
import psycopg2


class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("hello, welcome to [/test/]!")


class DBTestHandler_pg(tornado.web.RequestHandler):

	def pg_connection_setting(self):
		settings = {}
		settings['POSTGRES_SERVER'] = 'localhost'
		settings['POSTGRES_PORT'] = 5432
		settings['POSTGRES_DB'] = 'lcic_db'
		settings['POSTGRES_USER'] = 'lcic'
		settings['POSTGRES_PW'] = '123456'

		connection = psycopg2.connect(
				database= settings['POSTGRES_DB'],
				user= settings['POSTGRES_USER'],
				password= settings['POSTGRES_PW'],
				host= settings['POSTGRES_SERVER'],
				port= settings['POSTGRES_PORT'],
			)
		return connection

	def get(self):
		print self.request
		self.write("get success! but this Application work with POST method.")

	def post(self):

		url_type = self.get_argument('type')

		if url_type == "PushTaxiTrajectory":
			companyName = self.get_body_argument('companyName')
			dataName = 'trajectoryData'
			sql =  self.makesql(companyName, dataName, 'taxiNo', 'lat', 'lng', 'direction', 'speed', 'empty', **{'time': 'parse_time2str'})
			self.post_parse(companyName, dataName, *sql)

		elif url_type == "PushTaxiService":
			companyName = self.get_body_argument('companyName')
			dataName = 'serviceData'
			sql = self.makesql(companyName, dataName, 'taxiNo', 'money', **{'boardingTime': 'parse_time2str', 'alightingTime': 'parse_time2str'})
			self.post_parse(companyName, dataName, *sql)

	def makesql(self, companyName, dataName, *args, **kwargs):
		insert = "INSERT INTO %s_%s (" % (companyName, dataName)
		sql_keys = re.sub('[()\'"]','', str(args) + ',' + str(tuple(kwargs)))
		sql_keys = sql_keys[:-1] if sql_keys.endswith(',') else sql_keys  # kwargs -> when tuple has only one item, ('element',)
		total_s = '%s,' * (len(args) + len(kwargs))
		result_str = insert + sql_keys  + ') VALUES (' + total_s[:-1] + ');'
		all_args_list = []
		for i  in  args:
			all_args_list.append("item['" + i + "']")
		for (k,v)  in kwargs.items():
			all_args_list.append(v + "(item['" + k + "'])")
		return result_str, all_args_list


	def post_parse(self, companyName, dataName, sql, sql_var_lists):

		def parse_time2str(cs_json_time):
			# json获取的格式是 /Date(1480349734000)/ --这是C#的JavaScriptSerializer封装的格式
			time_secs = int(re.sub('\D', '', cs_json_time)[:-3])
			return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time_secs))

		# db Error: 'ascii' codec can't encode character u'\u5ddd' in position 101: ordinal not in range(128)
		reload(sys)
		sys.setdefaultencoding('utf-8')

		data = self.get_body_argument(dataName)

		# print self.request

		connection = self.pg_connection_setting()
		cursor = connection.cursor()
		datas = json.loads(data)
		print "===== load  %s items : " %  dataName, len(datas)
		
		for item in datas:
			# print item
			try:
				_sql = sql % tuple(map(lambda x: "'" + str(x) + "'", map(eval, sql_var_lists)))
				#print _sql
				cursor.execute(_sql )   
				#cursor.execute(cursor.mogrify(_sql) )   
				connection.commit()

			except Exception, e:
				connection.rollback()
				print "db Error: %s" % e




if __name__ == "__main__":
	application = tornado.wsgi.WSGIApplication(handlers =[
					(r"/", IndexHandler),
					(r"/test/receivedb", DBTestHandler_pg),
					#(r"/test/receivedb", DBTestHandler_mssql), 
					])
	server = gevent.wsgi.WSGIServer(("", 8000), application)
	server.serve_forever()