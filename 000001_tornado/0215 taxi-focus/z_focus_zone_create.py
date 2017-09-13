# -*- coding:utf-8 -*- 
# --------------------
# Author:		yh001
# Description:	
# --------------------

from tornado.escape import json_encode
import psycopg2
import time
import tornpg

def exe_time(func):
    def decorator(*args, **kwargs):
        start = time.time()
        back = func(*args, **kwargs)
        print('Function name:{0} {1}'.format(func.__name__, time.time() - start))
        return back
    return decorator


# def pg_connection_setting():
#     settings = {}
#     settings['POSTGRES_SERVER'] = 'localhost'
#     settings['POSTGRES_PORT'] = 5432
#     settings['POSTGRES_DB'] = 'lcic_db'
#     settings['POSTGRES_USER'] = 'lcic'
#     settings['POSTGRES_PW'] = '123456'

#     connection = psycopg2.connect(
#             database= settings['POSTGRES_DB'],
#             user= settings['POSTGRES_USER'],
#             password= settings['POSTGRES_PW'],
#             host= settings['POSTGRES_SERVER'],
#             port= settings['POSTGRES_PORT'],
#         )
#     return connection

# pg_connection = pg_connection_setting()
# connection =pg_connection
# cursor = connection.cursor()

# Postgres配置
POSTGRES_HOST = "121.42.154.40"
# POSTGRES_HOST = "127.0.0.1"
# POSTGRES_HOST = "222.85.152.47"
# POSTGRES_HOST = "localhost"
POSTGRES_USER = "lcic"
# POSTGRES_DB = "GyygDTDB"
# POSTGRES_PWD = "BY@gyyg1504"
POSTGRES_DB = "lcic_db"
POSTGRES_PWD = "123456"
POSTGRES_PORT = 5432
POSTGRES_URI = "postgresql://lcic:123456@121.42.154.40:5432/lcic_db"

psdb = tornpg.Connection(
    host=POSTGRES_HOST, database=POSTGRES_DB,
    user=POSTGRES_USER, password=POSTGRES_PWD, port=POSTGRES_PORT
)



# ndyd你大爷的，昨天都能运行，今天又不行了  =加个RETURNING id
@exe_time
def set_focus_zone_by_multipolygon(address, point_list, num):
    """
    (传入多边形坐标),生成聚集区域
    """
    pt_str = ''
    for point in point_list:
        pt_str += str(point.get('lng')) + ' ' + str(point.get('lat')) + ','
    pt_str = pt_str[:-1]
    multipolygon_str = 'MULTIPOLYGON(((' + pt_str + ')))'
    #print multipolygon_str

    try:
        id = psdb.insert('INSERT INTO dt_taxifocuszone(address, zone, num) '
                    'VALUES (%s, ST_Geomfromtext(%s, 4326), %s) RETURNING id', address, multipolygon_str, num)
        psdb.commit()
        #print id
        #print type(id) #tuple
    except Exception, e:
        print e
        psdb.rollback()




# 测试聚集热点区域

#贵阳火车站
GUIYANGHUOCHEZHAN = [{"lng":106.7109, "lat":26.5648},
                     {"lng":106.7117, "lat":26.5645},
                     {"lng":106.7109, "lat":26.5635},
                     {"lng":106.7098, "lat":26.5636},
                     {"lng":106.7109, "lat":26.5648},
                     ]


#解放路东（沙冲北路路口）
JIEFANGLUDONG = [{"lat":26.545721, "lng":106.706509},
                 {"lat":26.575862, "lng":106.729478},
                 {"lat":26.544609, "lng":106.728038},
                 {"lat":26.574672, "lng":106.715378},
                 {"lat":26.545721, "lng":106.706509},
                ]

# 延安东路
YANANDONGLU = [{"lng":106.718581, "lat":26.564021},
               {"lng":106.77542, "lat":26.59482},
               {"lng":106.774267, "lat":26.590993},
               {"lng":106.719394, "lat":26.568949},
               {"lng":106.718581, "lat":26.564021},
              ]


# 黄河北路环岛
HUANGHEBEILUHUANDAO = [{"lng":106.707775, "lat":26.530117},
                       {"lng":106.709731, "lat":26.532038},
                       {"lng":106.711288, "lat":26.528664},
                       {"lng":106.708869, "lat":26.528048},
                       {"lng":106.707775, "lat":26.530117},
                      ]

FOCUS_ALRAM_RULES = [
    {"address":"解放路东","point_list":JIEFANGLUDONG, "num":5},
    {"address":"延安东路","point_list":YANANDONGLU, "num":5},
]



if __name__ == "__main__":
    set_focus_zone_by_multipolygon(**{"address":"解放路东","point_list":JIEFANGLUDONG, "num":5})
    set_focus_zone_by_multipolygon("延安东路",YANANDONGLU, 5)


