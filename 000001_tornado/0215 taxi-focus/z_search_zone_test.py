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

@exe_time
def get_focus_zones_from_db():
    zone_list = psdb.query("SELECT address, zone, num  FROM dt_taxifocuszone")
    return zone_list

@exe_time
def get_points_by_zone(zone):
    """
    查询zone中包含的点(传入的zone为postgresql的geom对象字符串)
    'zone': '0106000020E610000001000000010300000001000000050000001955867
    137AD5A408CBD175FB48B3A40410C74ED0BAE5A40950C0055DC903A4042D2A755F4AD5A40761BD47
    E6B8B3A40C991CEC0C8AD5A4088F71C588E903A401955867137AD5A408CBD175FB48B3A40'

    """

    pt_list = psdb.query(
        "SELECT "
        "ST_X(pt) AS lng, "
        "ST_Y(pt) AS lat, "
        "vehicle_card, "
        "time "
        "FROM dt_vehiclegps "
        "WHERE "
        "ST_Contains(%s, pt)", zone
    )
    return pt_list

if __name__ == "__main__":
    zone_list = get_focus_zones_from_db()
    print zone_list
    """
    Function name:get_focus_zones_from_db 0.151999950409
    [{'num': 5, 'zone': '0106000020E610000001000000010300000001000000050000001955867
    137AD5A408CBD175FB48B3A40410C74ED0BAE5A40950C0055DC903A4042D2A755F4AD5A40761BD47
    E6B8B3A40C991CEC0C8AD5A4088F71C588E903A401955867137AD5A408CBD175FB48B3A40', 'add
    ress': u'\u89e3\u653e\u8def\u4e1c'}, {'num': 5, 'zone': '0106000020E610000001000
    00001030000000100000005000000BAA1293BFDAD5A40938B31B08E973A4051F701486DAE5A402B6
    A300DC3973A409CA4F9635AAE5A40392A37514B973A4012BC218D0AAE5A400C03965CC5963A40BAA
    1293BFDAD5A40938B31B08E973A40', 'address': u'\u5ef6\u5b89\u4e1c\u8def'}]
    """

    pt_list = get_points_by_zone(zone_list[-1].get('zone'))
    print pt_list


