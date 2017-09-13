# -*- coding:utf-8 -*- 
# --------------------
# Author:		yh001
# Description:	出租车
# --------------------

import functools
import time
import tornado.ioloop
from concurrent.futures import ThreadPoolExecutor
from tornado import gen
from tornado.concurrent import app_log
from tornado.concurrent import run_on_executor
from tornado.web import asynchronous

from tornado.escape import json_encode

from conf.constant import VEHICLE_TYPE
from .PublishMessageCache import ClientLoadedVehicleCache
from ..model import TaxiModel
from ..model.TaxiModel import taxi_model
from ...common.controller.base import BaseHandler

from modules.analysis.controller.TaxiFocusZoneCache import taxi_focus_zone_instance

from conf.constant import (TAXI_FOCUS_ZONE, 
                        TAXI_FOCUS_ZONE_EXPIRE_TIME, 
                        TAXI_FOCUS_ZONE_ALARM_TIME,
                        TAXI_FOCUS_START_TIME_KEY,
                        TAXI_FOCUS_ADDRESS_KEY)


class GetTaxiHandler(BaseHandler):
    """获取出租车信息"""

    def get(self):
        session_id = self.get_argument("session_id", "")

        info_json, vehicle_card_dict, vehicle_card_str = taxi_model.get_all_taxi()
        ClientLoadedVehicleCache.set_vehicle_loaded_card_and_type(
            session_id,
            VEHICLE_TYPE.get(3),  # "taxi",
            vehicle_card_dict,
            vehicle_card_str
        )

        self.write(info_json)


class GetTaxiFocusHandler(BaseHandler):
    """获取出租车聚集响应事件"""
    executor = ThreadPoolExecutor(1)
    started = False

    # @asynchronous
    # @gen.coroutine
    # 不需要，需要的是在model里面搞一个线程池？？
    def get(self, *args, **kwargs):
        if not GetTaxiFocusHandler.started:
            tornado.ioloop.IOLoop.instance().add_callback(
                functools.partial(self.update_focus_zone_from_redis)
            )
            GetTaxiFocusHandler.started = True
        taxi_focus_list = taxi_focus_zone_instance.get_all_taxi_focus_data()
        json_list = json_encode(taxi_focus_list)
        self.write(json_list)


    # def get(self):
    #     if not PublisherStartHandler.started:
    #         tornado.ioloop.IOLoop.instance().add_callback(
    #             functools.partial(self.get_msg_from_redis_queue)
    #         )
    #         PublisherStartHandler.started = True
    #         self.finish({"state": 0})
    #     else:
    #         self.finish({"state": 1})




    @run_on_executor
    def update_focus_zone_from_redis(self):
        """
        开个独立的线程池，每分钟运行一次查数据库，查出每个区域里面的车辆，对每个车辆做update_taxi_focus_by_vehicle_card
        貌似开销会很大吧？
        """
        zone_list = TaxiModel.get_focus_zones_from_db()

        t = taxi_focus_zone_instance
        t.init_taxi_foucs_redis_cache()

        t.update_taxi_focus_by_vehicle_card('lcic_taxi_focus_zone:35', '贵AU4531')
        t.update_taxi_focus_by_vehicle_card('lcic_taxi_focus_zone:35', '贵AU5970')
        t.update_taxi_focus_by_vehicle_card('lcic_taxi_focus_zone:34', '贵AU6776')
        print t.get_taxi_focus_cache_by_id(35)
        # print t.get_all_taxi_focus_data()
        print len(t.get_all_taxi_focus_data())

        while True:
            start_time = time.time()
            # for: 对每个区域get_points_by_zone
            for zone in zone_list:
                pt_list = TaxiModel.get_points_by_zone(zone.get('zone'))
                zone_id = zone.get('id')
                id_str = TAXI_FOCUS_ZONE + ':' + str(zone_id)
                # for: 对每个车辆做update_taxi_focus_by_vehicle_card
                for item in pt_list:
                    vehicle_card =  item['vehicle_card']
                    taxi_focus_zone_instance.update_taxi_focus_by_vehicle_card(id_str, vehicle_card)
                app_log.debug('update taxi focus zone: {0}, zone id={1}'.format(zone.get('address').encode("utf-8"), zone_id))
            run_time = time.time() - start_time
            time.sleep(60 - run_time)
            #保证每次循环运行时间为一分钟






