# -*- coding:utf-8 -*- 
# --------------------
# Author:       
# Description:   
# --------------------

MAX_BUFFER_SIZE = 4 * 1024**3 # 4GB

import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print __file__
print BASE_DIR
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates")  # 模板目录
STATIC_PATH = os.path.join(BASE_DIR, "static")  # 静态资源目录
UPLOAD_PATH = os.path.join(STATIC_PATH, "uploads")

# Postgres配置
# POSTGRES_HOST = "121.42.154.40"
POSTGRES_HOST = "127.0.0.1"
POSTGRES_USER = "test"
POSTGRES_DB = "lcic_db"
POSTGRES_PWD = "test"
POSTGRES_PORT = 5432

# MongoDB配置
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

# SETTINGS
SETTINGS = dict(
    template_path=TEMPLATE_PATH,
    static_path=STATIC_PATH,
    cookie_secret="MmvPLn19QXqz83Pq3miVtUwYSA6oi0YCuUI26RUA/LU=",
    xsrf_cookies=True,
    login_url="/auth/login",
    # debug=True,
    ui_modules={
    }
)


# Redis配置
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_URL = 'redis://@127.0.0.1:6379'


class RedisExpire(object):
    def __init__(self):
        pass

    SECOND_EXPIRE = 5  # 5秒释放
    MINUTE_EXPIRE = 60  # 1分钟释放
    HOUR_EXPIRE = 60 * 60  # 1小时释放
    DAY_EXPIRE = 24 * 60 * 60   # 1天释放


# CACHE KEY
LCIC_CACHE_KEY = 'lcic_cache:{0}'


VEHICLE_TYPE = {
    1: "freight_vehicle",  # 货运
    2: "danger_freight_vehicle",  # 危货
    3: "taxi",  # 出租车
    4: "passenger_vehicle",  # 客运车, 班线车
    5: "tourist_vehicle",  # 旅游班车
    6: "bus",  # 公交车
    7: "training_vehicle",  # 教练车
    8: "net_about_car",  # 网约车
}
VEHICLE_TYPE_REVERSE = {
    "freight_vehicle": "1",  # 货运
    "danger_freight_vehicle": "2",  # 危货
    "taxi": "3",  # 出租车
    "passenger_vehicle": "4",  # 客运车, 班线车
    "tourist_vehicle": "5",  # 旅游班车
    "bus": "6",  # 公交车
    "training_vehicle": "7",  # 教练车
    "net_about_car": "8",  # 网约车
}

# 数据推送操作类型
ACTION = {
    "update": "update",
    "insert": "insert",
    "delete": "delete"
}

# CACHE KEY
LCIC_CACHE_KEY = 'lcic_cache:{0}'

# CACHE EXPIRE
MINUTE = 60
HALF_HOUR = 60 * 30
HOUR = 60 * 60
HALF_DAY = 60 * 60 * 12
DAY = 60 * 60 * 24
# 车辆当前位置过期时间, 过期没有更新将从地图上移除
VEHICLE_EXPIRE_SECOND = 60 * 10

# Redis key
GPS_QUEUE_KEY = "lcic_gps_queue:key"  # 车辆GPS实时信息队列KEY
VEHICLE_TYPE_GPS_KEY = "lcic_vehicle_type_gps:key"  # 包含车辆类型的GPS信息缓存KEY
CLIENT_STATE_KEY = "lcic_client_state:key"  # 客户端状态信息KEY
VEHICLE_LOADED_KEY = "lcic_vehicle_loaded:"  # 客户端已加载的车辆KEY

ALL_VEHICLE_INFO_CACHE = "lcic_all_vehicle_info:key"  # 所有车辆详情信息缓存
DANGER_FREIGHT_VEHICLE_INFO_CACHE = "lcic_danger_freight_vehicle_info_cache:key"  # 危货车辆详情信息缓存KEY
TAXI_INFO_CACHE = "lcic_taxi_info_cache:key"  # 出租车详情信息缓存KEY
PASSENGER_VEHICLE_INFO_CACHE = "lcic_passenger_vehicle_cache:key"  # 客运车辆详情信息缓存KEY
TOURIST_VEHICLE_INFO_CACHE = "lcic_tourist_vehicle_info_cache:key"  # 旅游班车详情信息缓存KEY

LAW_PEOPLE_INFO_CACHE = "lcic_law_people_info_cache:key"  # 执法个员详情缓存KEY
LAW_VEHICLE_INFO_CACHE = "lcic_law_vehicle_info:cache:key"  # 执法车辆详情信息缓存KEY
LAW_HOT_SPOT_INFO_CACHE = "lcic_law_hot_spot_info:cache:key"  # 行政执法缓存数据（执法热点)
LAW_ENFORCEMENT_NUM_INFO_CACHE = "lcic_law_enforcement_num_info:cache:key"  # 行政执法缓存数据（执法数量)
LAW_ANALYSIS_INFO_CACHE = "lcic_law_analysis_info:cache:key"  # 行政执法缓存数据（执法分析)

TAXI_FOCUS_ZONE = "lcic_taxi_focus_zone"
TAXI_FOCUS_START_TIME_KEY = 'lcic_taxi_focus_zone_start_time:key'
TAXI_FOCUS_ADDRESS_KEY = 'lcic_taxi_focus_zone_id:address'
TAXI_FOCUS_ADDRESS_RULE_KEY = 'lcic_taxi_focus_zone_id:rule'
TAXI_FOCUS_ZONE_EXPIRE_TIME = 30  * 48  # 为了测试的需要，加了个系数, 则时间为1天
TAXI_FOCUS_ZONE_ALARM_TIME = 10  / 5  # 为了测试的需要，加了个系数
