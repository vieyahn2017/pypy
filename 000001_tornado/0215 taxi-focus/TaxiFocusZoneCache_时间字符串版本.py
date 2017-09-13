# -*- coding:utf-8 -*- 
# --------------------
# Author:		yh001
# Description:	消息实时推送及缓存相关操作.
# Time: 2017-2-16
# --------------------

import datetime
from tornado.escape import json_encode, json_decode
from tornado.log import app_log

from conf.constant import (TAXI_FOCUS_ZONE, 
                        TAXI_FOCUS_ZONE_EXPIRE_TIME, 
                        TAXI_FOCUS_ZONE_ALARM_TIME)


from modules.analysis.model import TaxiModel
from modules.common.model.dbManager import rsdb


class TaxiFocusZoneCache(object):
    """
    先从数据库读入所有区域
    再读取每个区域存在的点，缓存入redis
    再写个实时更新redis值的方法--在TaxiHandler里用线程池运行
    """

    def __init__(self, server):
        self.server = server
        self.hash_key = TAXI_FOCUS_ZONE
        self.expire_time = TAXI_FOCUS_ZONE_EXPIRE_TIME
        self.alarm_time = TAXI_FOCUS_ZONE_ALARM_TIME

    def flush_all_elder_redis_key(self):
        """
        Call this method before cache.Flush all redis key of taxi-focus.
        """
        lcic_key_list = self.server.keys(self.hash_key + '*')
        if lcic_key_list:
            app_log.debug('Flush elder taxi-focus redis key:{0}'.format(lcic_key_list))
            self.server.delete(*lcic_key_list)

    def init_taxi_foucs_redis_cache(self):
        """
        Cache taxi focus zone initialize: read data from dt_vehiclegps table
        Cache redis hkey >> TAXI_FOCUS_ZONE + id 
        eg. "lcic_taxi_focus_zone:1"

        >>>redis-cli command:
        hlen lcic_taxi_focus_zone:1
        hgetall lcic_taxi_focus_zone:1
        hget lcic_taxi_focus_zone:1 "\xe8\xb4\xb5AU4803"
        """
        self.flush_all_elder_redis_key()

        focus_zone_list = TaxiModel.get_focus_zones_from_db()
        for item in focus_zone_list:
            zone_id = item.get('id')
            pt_list = TaxiModel.get_points_by_zone(item.get('zone'))
            if pt_list:
                for pt in pt_list:
                    focus_zone_hkey = self.hash_key + str(zone_id)
                    self.server.hset(
                        focus_zone_hkey,
                        pt.get('vehicle_card'),
                        pt.get('time')
                    )
                    print pt.get('time'), type(pt.get('time'))
                app_log.debug('Taxi focus zone cache initialize: {0}, the redis hkey is {1}, hlen={2}'.format(
                                item.get('address').encode("utf-8"), 
                                focus_zone_hkey,
                                len(pt_list)
                            ))


    def update_taxi_focus_cache_by_hkey(self, hkey, pt_list):
        """
        # 先清空吗? 这个方法设计的本意是， 用pt_list整个完全更新该hkey
        pt_list =
        [{'lat': 26.5645, 'vehicle_card': u'\u8d35A49860', 'lng': 106.72571, 'time': datetime.datetime(2017, 2, 16, 13, 53, 1)}, 
        {'lat': 26.552484, 'vehicle_card': u'\u8d35AT1428', 'lng': 106.727449, 'time': datetime.datetime(2017, 2, 16, 13, 53, 57)}]
        """
        self.server.delete(hkey)
        for pt in pt_list:
            self.server.hset(hkey, pt.get('vehicle_card'), pt.get('time'))
        app_log.debug('update Taxi focus zone cache: {0}, len={1}, at:{2}'.format(
                        hkey, len(pt_list), datetime.datetime.now()))


    def update_taxi_focus_cache_by_id(self, id, pt_list):
        focus_zone_hkey = self.hash_key + str(id)
        self.update_taxi_focus_cache_by_hkey(focus_zone_hkey, pt_list)


    def get_taxi_focus_cache_by_hkey(self, hkey):
        """
        hgetall lcic_taxi_focus_zone:1
        return type: dict
        {'\xe8\xb4\xb5AUA903': '2017-01-25 01:23:58', '\xe8\xb4\xb5AT2099': '2017-02-12 19:00:52', ...}
        """
        items = self.server.hgetall(hkey)
        return items


    def get_taxi_focus_cache_by_id(self, id):
        """
        hgetall lcic_taxi_focus_zone:id
        解放路东 id=34
        """
        focus_zone_hkey = self.hash_key + str(id)
        return self.get_taxi_focus_cache_by_hkey(focus_zone_hkey)


    def update_taxi_focus_by_time(self, time=None):

        if time is None:
            time = datetime.datetime.now() - datetime.timedelta(minutes = TAXI_FOCUS_ZONE_EXPIRE_TIME) #hours=1

        focus_zone_list = TaxiModel.get_focus_zones_from_db()
        for item in focus_zone_list:
            zone_id = item.get('id')
            pt_list = TaxiModel.get_points_by_zone(item.get('zone'), time)
            print pt_list
            if pt_list:
                for pt in pt_list:
                    focus_zone_hkey = self.hash_key + str(zone_id)
                    self.server.hset(
                        focus_zone_hkey,
                        pt.get('vehicle_card'),
                        pt.get('time')
                    )
                app_log.debug('Taxi focus zone cache initialize: {0}, the redis hkey is {1}, hlen={2}'.format(
                                item.get('address').encode("utf-8"), 
                                focus_zone_hkey,
                                len(pt_list)
                            ))


taxi_focus_zone_instance = TaxiFocusZoneCache(rsdb)
