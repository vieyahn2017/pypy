# -*- coding:utf-8 -*- 


class TaxiFocusZoneCache(object):
    """
    先从数据库读入所有区域
    再读取每个区域存在的点，缓存入redis
    再写个实时更新redis的方法--在TaxiHandler里用线程池运行
    """

    def __init__(self, server):
        self.server = server
        self.monitor_key = TAXI_FOCUS_ZONE
        self.expire_time = TAXI_FOCUS_ZONE_EXPIRE_TIME
        self.alarm_time = TAXI_FOCUS_ZONE_ALARM_TIME

    def init_redis_cache(self):