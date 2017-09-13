# -*- coding:utf-8 -*- 
# --------------------
# Author:		yh001
# Description:	
# --------------------
from tornado.log import app_log
from modules.common.model.dbManager import psdb
from tornado.escape import json_encode
from conf.constant import VEHICLE_TYPE
from .BaseModel import AnalysisBaseModel

def get_points_by_multipolygon(point_list):
    """
    查询多边形中包含的点(传入多边形坐标)
    eg: point_list [{"lng":1, "lat":2},{"lng":4, "lat":5}]

    #经验证，比上面的LINESTRING要快一倍
    """
    pt_str = ''
    for point in point_list:
        pt_str += str(point.get('lng')) + ' ' + str(point.get('lat')) + ','
    pt_str = pt_str[:-1]
    multipolygon_str = 'MULTIPOLYGON(((' + pt_str + ')))'

    pt_list = psdb.query(
        "SELECT "
        "ST_X(pt) AS lng, "
        "ST_Y(pt) AS lat, "
        "vehicle_card, "
        "time "
        "FROM dt_vehiclegps "
        "WHERE "
        "ST_Contains(ST_Geomfromtext(%s, 4326), pt)", multipolygon_str
    )
    return pt_list


def set_focus_zone_by_multipolygon(address, point_list, num):
    """
    (传入多边形坐标),生成聚集区域
    """
    pt_str = ''
    for point in point_list:
        pt_str += str(point.get('lng')) + ' ' + str(point.get('lat')) + ','
    pt_str = pt_str[:-1]
    multipolygon_str = 'MULTIPOLYGON(((' + pt_str + ')))'

    try:
        psdb.insert('INSERT INTO dt_taxifocuszone(address, zone, num) '
                    'VALUES (%s, ST_Geomfromtext(%s, 4326), %s) ', address, multipolygon_str, num)
        psdb.commit()
    except Error as e:
        print e
        psdb.rollback()

def get_focus_zones_from_db():
    """从db读取预设的聚集区"""
    zone_list = psdb.query("SELECT id, address, zone, num  FROM dt_taxifocuszone")
    return zone_list

def get_points_by_zone(zone, time=None):
    """
    查询zone中包含的点(传入的zone为postgresql的geom对象字符串)
    'zone': '0106000020E610000001000000010300000001000000050000001955867
    137AD5A408CBD175FB48B3A40410C74ED0BAE5A40950C0055DC903A4042D2A755F4AD5A40761BD47
    E6B8B3A40C991CEC0C8AD5A4088F71C588E903A401955867137AD5A408CBD175FB48B3A40'
    很明显这种zone是别的方法生成（从数据库读出来）的，不可能靠手动传入
    """
    # sql还需要添加条件 sync_type=1
    if time is None:
        pt_list = psdb.query(
            "SELECT ST_X(pt) AS lng, ST_Y(pt) AS lat, vehicle_card, time "
            "FROM dt_vehiclegps "
            "WHERE ST_Contains(%s, pt)", zone
        )
        return pt_list
    else:
        pt_list = psdb.query(
            "SELECT ST_X(pt) AS lng, ST_Y(pt) AS lat, vehicle_card, time "
            "FROM dt_vehiclegps "
            "WHERE ST_Contains(%s, pt) "
            "AND time > %s ", zone, time            
        )
        return pt_list

class TaxiModel(AnalysisBaseModel):
    def get_all_taxi(self):
        """获取出租车信息"""
        pt_list = self.server.query(
            'SELECT '
            'ST_X(pt) AS lng, '
            'ST_Y(pt) AS lat, '
            'dt_vs.vehicle_card AS vehicle_card '
            'FROM dt_vehiclegps AS dt_vs '
            'LEFT JOIN view_ct_vehicle_card AS dt_vc '
            'ON dt_vs.vehicle_card = dt_vc.vehicle_card '
            'WHERE dt_vc.vehiclepropertyid = 3 '
        )

        app_log.debug('Taxi: {0}'.format(len(pt_list)))
        return self.pt_wgs84_to_bd09(pt_list, VEHICLE_TYPE.get(3))

    def get_taxi_focus(self):
        """
        获取出租车聚集响应事件
        这是第一版，直接从数据库取出数据，如果num大于就传给前端
        现在改在TaxiFocusZoneCache去实现了
        也就是说以前TaxiHandler是调用的这里的get_taxi_focus,
        现在调用的是那边的方法taxi_focus_zone_instance.get_all_taxi_focus_data()
        这边暂时保留
        """
        taxi_focus_list = []
        zone_list = get_focus_zones_from_db()
        for rule in zone_list:
            pt_list = get_points_by_zone(rule.get('zone'))
            if len(pt_list) > rule.get('num'):
                app_log.debug('Taxi Focus Alarm: {0}, the Rule at {1} is {2}'.format(len(pt_list), rule.get('address').encode("utf-8"), rule.get('num')))
                for item in pt_list:
                    item['address'] = rule.get('address')
                    item['time'] = str(item['time'])
                    taxi_focus_list.append(item)
        return taxi_focus_list



taxi_model = TaxiModel()
