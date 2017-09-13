# -*- coding:utf-8 -*- 
# --------------------
# Author:		Ken
# Description:	系统入口
# --------------------
import tornado.options
from tornado import httpserver, ioloop, web
from tornado.log import app_log
from tornado.options import define, options

from conf.config import SETTINGS
from modules.analysis.controller.PublishMessageCache import (lcic_cache_instance,
                                                             vehicle_monitor_instance)
from modules.analysis.controller.TaxiFocusZoneCache import taxi_focus_zone_instance

from router import HANDLERS

define("port", default=9030, help="default run port", type=int)
# define("log_file_prefix", default="tornado.log", help="log file prefix")
options.logging = "debug"
options.log_to_stderr = True


# APP
class Application(web.Application):
    def __init__(self):
        handlers = HANDLERS
        settings = SETTINGS
        super(Application, self).__init__(handlers, **settings)


# Main入口
if __name__ == '__main__':
    tornado.options.parse_command_line()
    app_log.info('Vehicle type gps info cache to redis...')
    #lcic_cache_instance.lcic_start_cache()
    #vehicle_monitor_instance.init_vehicle_expire()

    #import datetime
    # t = taxi_focus_zone_instance

    # t.init_taxi_foucs_redis_cache()
    # print t.get_taxi_focus_start_time()
    # print t.get_taxi_focus_mins_from_start_time()

    # pt_list = [{'lat': 26.5645, 'vehicle_card': u'\u8d35A49860', 'lng': 106.72571, 'time': datetime.datetime(2017, 2, 16, 13, 53, 1)}, 
    #     {'lat': 26.552484, 'vehicle_card': u'\u8d35AT1428', 'lng': 106.727449, 'time': datetime.datetime(2017, 2, 16, 13, 53, 57)}]
    # t.update_taxi_focus_cache_by_id(35, pt_list)
    
    # t.update_taxi_focus_by_vehicle_card('lcic_taxi_focus_zone:35', '贵AU4531')
    # t.update_taxi_focus_by_vehicle_card('lcic_taxi_focus_zone:35', '贵AU5970')
    # t.update_taxi_focus_by_vehicle_card('lcic_taxi_focus_zone:34', '贵AU6776')
    # print t.get_taxi_focus_cache_by_id(35)
    # print t.get_all_taxi_focus_data()
    #print t.get_time_minutes_from_start_time(20)


    app_log.info('Listen on port 9030...')
    http_server = httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    ioloop.IOLoop.current().start()
