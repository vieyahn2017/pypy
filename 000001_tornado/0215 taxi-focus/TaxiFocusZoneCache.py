# -*- coding:utf-8 -*- 
# --------------------
# Author:		yh001
# Description:	消息实时推送及缓存相关操作.
# Time: 2017-2-16
# --------------------

import datetime
import time
from itertools import chain
from tornado.escape import json_encode, json_decode
from tornado.log import app_log

from modules.analysis.model import TaxiModel
from modules.common.model.dbManager import rsdb

from conf.constant import (TAXI_FOCUS_ZONE, 
                        TAXI_FOCUS_ZONE_EXPIRE_TIME, 
                        TAXI_FOCUS_ZONE_ALARM_TIME,
                        TAXI_FOCUS_START_TIME_KEY,
                        TAXI_FOCUS_ADDRESS_KEY,
                        TAXI_FOCUS_ADDRESS_RULE_KEY)

class TaxiFocusZoneCache(object):
    """
    先从数据库读入所有区域
    再读取每个区域存在的点，缓存入redis
    再写个实时更新redis值的方法--在TaxiHandler里用线程池运行
    """

    def __init__(self, server):
        self.server = server
        self.hash_key = TAXI_FOCUS_ZONE + ':'
        self.expire_time = TAXI_FOCUS_ZONE_EXPIRE_TIME
        self.alarm_time = TAXI_FOCUS_ZONE_ALARM_TIME
        self.start_time = TAXI_FOCUS_START_TIME_KEY
        self.address_key = TAXI_FOCUS_ADDRESS_KEY
        self.rule_key = TAXI_FOCUS_ADDRESS_RULE_KEY


    def flush_all_elder_redis_key(self):
        """
        Call this method before cache.
        Flush all redis key of taxi-focus.
        """
        lcic_key_list = self.server.keys(self.hash_key + '*')
        if lcic_key_list:
            app_log.debug('Flush elder taxi-focus redis key:{0}'.format(lcic_key_list))
            self.server.delete(*lcic_key_list)


    def init_taxi_foucs_redis_cache(self):
        """
        Cache taxi focus zone initialize: read data from dt_vehiclegps table.
        Cache redis hkey >> TAXI_FOCUS_ZONE + id 
        eg. "lcic_taxi_focus_zone:1"

        >>>redis-cli command:
        get "lcic_taxi_focus_zone_start_time:key"
        # taxi focus cache start_time
        hgetall "lcic_taxi_focus_zone_id:address"
        # id & address 映射表
        hgetall "lcic_taxi_focus_zone_id:rule"
        # id & rule-num 映射表
        hlen lcic_taxi_focus_zone:1
        hgetall lcic_taxi_focus_zone:1
        hget lcic_taxi_focus_zone:1 "\xe8\xb4\xb5AU4803"
        # 每个id缓存一个区域
        """
        self.flush_all_elder_redis_key()
        t_now = datetime.datetime.now()
        self.server.set(self.start_time, t_now.strftime("%Y-%m-%d %H:%M:%S"))

        focus_zone_list = TaxiModel.get_focus_zones_from_db()
        for item in focus_zone_list:
            zone_id = item.get('id')
            focus_zone_hkey = self.hash_key + str(zone_id)
            self.server.hset(
                            self.address_key,
                            focus_zone_hkey,
                            item.get('address'))
            self.server.hset(
                            self.rule_key,
                            focus_zone_hkey,
                            item.get('num'))            
            pt_list = TaxiModel.get_points_by_zone(item.get('zone'))
            if pt_list:
                remain_pt = 0
                for pt in pt_list:
                    sep_day = (t_now - pt.get('time')).days
                    # 停留大于1天的舍去；剩余的全部初始化为0
                    if sep_day < 1:
                        self.server.hset(
                            focus_zone_hkey,
                            pt.get('vehicle_card'),
                            0
                        )
                        remain_pt += 1
                app_log.debug('initialize cache: {0}, redis_hkey: [{1}], list_len={2} / remain={3}'.format(
                                item.get('address').encode("utf-8"), 
                                focus_zone_hkey,
                                len(pt_list),
                                remain_pt
                            ))


    def get_taxi_focus_rule_of_hkey(self, hkey):
        """"Get taxi-focus rule-num of zone hkey """
        return int(self.server.hget(self.rule_key, hkey))


    def get_taxi_focus_start_time(self):
        """"Get taxi-focus start time from redis cache. format is str of datetime """
        t_time = self.server.get(self.start_time)
        p_time = datetime.datetime.strptime(t_time, "%Y-%m-%d %H:%M:%S")
        return p_time


    def get_taxi_focus_mins_from_start_time(self):
        """Get the minutes from start time of redis cache"""
        t = datetime.datetime.now() - self.get_taxi_focus_start_time()
        # datetime.timedelta 有.days() .total_seconds() 没有分钟，小时的方法
        return int(t.total_seconds()) / 60


    def get_time_from_start_by_mins(self, mins):
        """Get the time from start time of redis cache by parameter: mins"""
        start_time = self.get_taxi_focus_start_time()
        result_time = start_time + datetime.timedelta(minutes = mins)
        return str(result_time)


    def update_taxi_focus_by_vehicle_card(self, hkey, vehicle_card):
        """
        按照车牌号，实时更新redis缓存
        开个独立的线程池，每分钟运行一次查数据库，查出每个区域里面的车辆，
        对每个车辆做update_taxi_focus_by_vehicle_card
        貌似开销会很大吧？
        """
        mins = self.get_taxi_focus_mins_from_start_time()
        if mins > self.expire_time:
            mins = self.expire_time
        # 超出时间的，统一截取
        if self.server.hexists(hkey, vehicle_card):
            self.server.hset(hkey, vehicle_card, mins)
        else:
            self.server.hset(hkey, vehicle_card, 0)


    def get_taxi_focus_cache_by_hkey(self, hkey):
        """
        hgetall lcic_taxi_focus_zone:1
        return type: dict 
        {'\xe8\xb4\xb5AUA903': '2017-01-25 01:23:58', '\xe8\xb4\xb5AT2099': '2017-02-12 19:00:52', ...}
        return: # 最新 把值从时间改成分钟了
        {'\xe8\xb4\xb5AUA903': 33, '\xe8\xb4\xb5AT2099': 10, ...}
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


    def get_taxi_focus_data_by_hkey(self, hkey):
        """
        获取指定hkey的聚集区的数据，并包装为传给前端的list
        只保留停留时长int(items[item]) > self.alarm_time的
        """
        items = self.get_taxi_focus_cache_by_hkey(hkey)
        res = []
        for item in items:
            if int(items[item]) > self.alarm_time:
                data = {}
                data['vehicle_card'] = item
                data['address'] = self.server.hget(self.address_key, hkey)
                data['time'] = self.get_time_from_start_by_mins(int(items[item]))
                res.append(data)
        rule_num = self.get_taxi_focus_rule_of_hkey(hkey)
        if len(res) > rule_num:
            address= self.server.hget(self.address_key, hkey)
            app_log.debug('Taxi focus alarm at: {0}, the Rule is {1}, now focus up to {2}'.format(
                address, #address.encode("utf-8"), 
                rule_num, 
                len(res)
            ))
            return res
        else:
            return None


    def get_taxi_focus_data_by_id(self, id):
        """
        获取指定id的聚集区的数据，并包装为传给前端的list
        """
        focus_zone_hkey = self.hash_key + str(id)
        return self.get_taxi_focus_data_by_hkey(focus_zone_hkey)


    def get_all_taxi_focus_data(self):
        """
        获取所有的聚集区，并取出其中的数据
        from itertools import chain 用来合并list
        s = [[1, 2, 3], [4, 5], [6, 7]]
        list(chain(*s))
        """
        hkey_list = self.server.keys(self.hash_key + '*')
        datas = []
        for hkey in hkey_list:
            data = self.get_taxi_focus_data_by_hkey(hkey)
            if data:
                datas.append(data)
        return list(chain(*datas))


    def update_taxi_focus_cache_by_hkey(self, hkey, pt_list):
        """
        # 先清空吗? 这个方法设计的本意是， 用pt_list整个完全更新该hkey. 
        # 这样或许不妥，暂时不走这样的思路
        pt_list =
        [{'lat': 26.5645, 'vehicle_card': u'\u8d35A49860', 'lng': 106.72571, 'time': datetime.datetime(2017, 2, 16, 13, 53, 1)}, 
        {'lat': 26.552484, 'vehicle_card': u'\u8d35AT1428', 'lng': 106.727449, 'time': datetime.datetime(2017, 2, 16, 13, 53, 57)}]
        """
        self.server.delete(hkey)
        for pt in pt_list:
            self.server.hset(hkey, pt.get('vehicle_card'), pt.get('time'))
        app_log.debug('update Taxi focus zone cache: {0}, len={1}, at:{2}'.format(
                        hkey, len(pt_list), datetime.datetime.now()))


    def update_taxi_focus_by_expire_time(self):
        """
        统一对所有的聚集区，按照expire_time更新数据
        超出的时间截出
        # 这样或许不妥，暂时不走这样的思路，下面的代码不完善，暂时保留吧
        """

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
