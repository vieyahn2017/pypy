# -*- coding:utf-8 -*- 
# --------------------
# Author:		gxm1015@qq.com
# Description:	
# --------------------
import datetime

from tornado.escape import json_encode
from tornado.log import app_log

from config import VEHICLE_TYPE, VEHICLE_EXPIRE_SECOND
from db.dbManager import psdb
from ..utils.coordTransform import wgs84_to_bd09

class AnalysisBaseModel(object):
    """
    Base Class for Analysis Model.
    It contains some reusable method.
    Other model in analysis can inherit from this class.
    """

    def __init__(self, server=psdb):
        self.server = server

    def pt_wgs84_to_bd09(self, query_result_list, vehicle_type_str):
        """
        This method is used for convert wgs84 point to bd09 point
        and get vehicle is status(activate or not).
        :param query_result_list: a query result list from postgres which need convert.
        :param vehicle_type_str: vehicle's type str
        :return: a tuple contains:
            a converted pt_list,
            a vehicle_card_dict used for loaded vehicle cache.
        """
        pt_bd09 = []
        vehicle_card_dict = {}
        for pt in query_result_list:
            bd09_lng, bd09_lat = wgs84_to_bd09([(pt.lng, pt.lat)])
            vehicle_card_dict[pt.vehicle_card] = pt.vehicle_card
            vehicle_info_item = {
                'lng': bd09_lng,
                'lat': bd09_lat,
                'vehicle_card': pt.vehicle_card
            }
            pt_bd09.append(
                self._set_vehicle_status(
                    pt['update_time'],
                    vehicle_info_item
                )
            )
        pt_dict = {'type': vehicle_type_str, "data": pt_bd09}
        return pt_dict, vehicle_card_dict

    def _set_vehicle_status(self, update_time, vehicle_info_item):
        """
        If vehicle did not update location in VEHICLE_EXPIRE_SECOND,
        set is_activate status to False else True.
        :param vehicle_info_item:
        :return:
        """
        now_time = datetime.datetime.now()
        time_obj = now_time - datetime.timedelta(seconds=VEHICLE_EXPIRE_SECOND)
        if update_time < time_obj:
            vehicle_info_item["is_activate"] = False
        else:
            vehicle_info_item["is_activate"] = True
        return vehicle_info_item




class PublishMessageCacheModel(AnalysisBaseModel):

    def get_all_vehicle_type_gps_info(self):
        """
        Get all vehicle's type, gps info from postgres.
        :return: a dict that redis can do hmset()
        """
        vehicle_info_dict = {}
        data_lists = self.server.query(
            "SELECT v_ct_vd.vehiclepropertyid AS type_id, "
            "ST_X(pt) as lng, "
            "ST_Y(pt) AS lat, "
            "v_ct_vd.vehicle_card, "
            "dt_vs.speed, "
            "dt_vs.direction, "
            "dt_vs.time, "
            "dt_vs.is_empty "
            "FROM view_ct_vehicle_card as v_ct_vd "
            "LEFT JOIN dt_vehiclegps  AS dt_vs "
            "ON dt_vs.vehicle_card=v_ct_vd.vehicle_card "
        )
        for data in data_lists:
            if data["type_id"]:
                bd09_pt = None
                if data["lng"] and data["lat"]:
                    bd09_pt = wgs84_to_bd09(
                        [(data["lng"], data["lat"])]
                    )
                data_dict = {
                    "type": VEHICLE_TYPE[data["type_id"]],
                    "action": 'update',  # default is update
                    "data": {
                        "vehicle_card": data["vehicle_card"],
                        "lng": float(bd09_pt[0]) if bd09_pt else 0,
                        "lat": float(bd09_pt[1]) if bd09_pt else 0,
                        "speed": float(data["speed"]) if data["speed"] else 0,
                        "direction": float(data["direction"]) if data["direction"] else 0,
                        "time": str(data["time"]),
                        "is_empty": data["is_empty"]
                    }
                }
                vehicle_info_dict[data['vehicle_card']] = json_encode(data_dict)
            else:
                # XXX:No type vehicle process?
                # app_log.warn(u'Vehicle card {0}\'s type is None'.format(data["vehicle_card"]))
                pass
        app_log.debug('Vehicle type map have {0} items will cache to redis'.
                      format(len(vehicle_info_dict)))
        return vehicle_info_dict

    def get_all_vehicle_info(self):
        """Get all vehicle info used to cache to redis"""
        # TODO: 排量, 核定载客载货? 驾照号码?
        vehicle_info_dict = {}
        data_list = self.server.query(
            "SELECT "
            "v_ct_vd.vehicle_card AS vehicle_card, "  # 车牌号码
            "v_ct_vd.vehiclepropertyid AS vehicle_type_id, "  # 车辆类型ID
            "ct_voe.vehicleoiltype AS oil_type, "  # 燃油类型
            "pt_cr_ck.name AS driver_name, "  # 驾驶员姓名
            "pt_cr_ck.idcard AS driver_id_card, "  # 驾驶员身份证号
            "pt_cr_ck.mobilephone AS driver_phone,"  # 驾驶员联系方式
            "pt_cr_ck.gender AS driver_sex, "  # 驾驶员性别
            "pt_cr_ck.vehiclepermitted AS driving_license_type, "  # 驾照类型
            "et_pr.proprietorname AS proprietor_name,"  # 业户名称
            "et_pr.linkman AS proprietor_linkman,"  # 业户联系人
            "et_pr.linkphone AS proprietor_link_phone,"  # 业户联系电话
            "et_pr.address AS proprietor_address "  # 业户地址
            "FROM "
            "view_ct_vehicle_card AS v_ct_vd "
            "LEFT JOIN pt_careervehicle AS pt_ce "
            "ON v_ct_vd.id = pt_ce.vehicleid "
            "LEFT JOIN "

            "(SELECT pt_career.id,"
            "pt_career.name,"
            "pt_career.idcard,"
            "pt_career.mobilephone,"
            "pt_career.gender,"
            "pt_career.vehiclepermitted "
            "FROM pt_career "
            "LEFT JOIN pt_career_check   "
            "ON pt_career.id = pt_career_check.careerid) "
            "AS pt_cr_ck "

            "ON pt_ce.careerid = pt_cr_ck.id "
            "LEFT JOIN ct_vehicleoiltype AS ct_voe "
            "ON ct_voe.id = v_ct_vd.oiltypeid "
            "LEFT JOIN et_proprietor AS et_pr "
            "ON et_pr.id = v_ct_vd.proprietorbaseid "

            "WHERE v_ct_vd.vehiclepropertyid = 2 OR "
            "v_ct_vd.vehiclepropertyid = 3 OR "
            "v_ct_vd.vehiclepropertyid = 4 OR "
            "v_ct_vd.vehiclepropertyid = 5 OR "
            "v_ct_vd.vehiclepropertyid = 7 "
        )
        for data in data_list:
            data_dict = {
                "vehicle_card": data.vehicle_card,
                "vehicle_type": VEHICLE_TYPE.get(data.vehicle_type_id),
                "oil_type": data.oil_type,
                "driver_name": data.driver_name,
                "driver_id_card": data.driver_id_card,
                "driver_phone": data.driver_phone,
                "driver_sex": data.driver_sex,
                "driving_license_type": data.driving_license_type,
                "proprietor_name": data.proprietor_name,
                "proprietor_linkman": data.proprietor_linkman,
                "proprietor_link_phone": data.proprietor_link_phone,
                "proprietor_address": data.proprietor_address
            }
            vehicle_info_dict[data['vehicle_card']] = json_encode(data_dict)
        app_log.debug("{0} vehicle info items will cache to redis".
                      format(len(vehicle_info_dict)))
        return vehicle_info_dict

    def get_all_danger_freight_vehicle_info(self):
        """Get all danger freight vehicle info used to cache to redis"""
        # TODO
        vehicle_info_dict = {}
        data_list = self.server.query(
            "SELECT "
            "v_ct_vd.vehicle_card AS vehicle_card, "  # 车牌号码
            "ct_voe.vehicleoiltype AS oil_type, "  # 燃油类型
            "pt_cr_ck.name AS driver_name, "  # 驾驶员姓名
            "pt_cr_ck.idcard AS driver_id_card, "  # 驾驶员身份证号
            "pt_cr_ck.mobilephone AS driver_phone,"  # 驾驶员联系方式
            "pt_cr_ck.gender AS driver_sex, "  # 驾驶员性别
            "pt_cr_ck.vehiclepermitted AS driving_license_type, "  # 驾照类型
            "et_pr.proprietorname AS proprietor_name,"  # 业户名称
            "et_pr.linkman AS proprietor_linkman,"  # 业户联系人
            "et_pr.linkphone AS proprietor_link_phone,"  # 业户联系电话
            "et_pr.address AS proprietor_address "  # 业户地址
            "FROM "
            "view_ct_vehicle_card AS v_ct_vd "
            "LEFT JOIN pt_careervehicle AS pt_ce "
            "ON v_ct_vd.id = pt_ce.vehicleid "
            "LEFT JOIN "

            "(SELECT pt_career.id,"
            "pt_career.name,"
            "pt_career.idcard,"
            "pt_career.mobilephone,"
            "pt_career.gender,"
            "pt_career.vehiclepermitted "
            "FROM pt_career "
            "LEFT JOIN pt_career_check   "
            "ON pt_career.id = pt_career_check.careerid) "
            "AS pt_cr_ck "

            "ON pt_ce.careerid = pt_cr_ck.id "
            "LEFT JOIN ct_vehicleoiltype AS ct_voe "
            "ON ct_voe.id = v_ct_vd.oiltypeid "
            "LEFT JOIN et_proprietor AS et_pr "
            "ON et_pr.id = v_ct_vd.proprietorbaseid "

            "WHERE v_ct_vd.vehiclepropertyid = 2"
        )
        for data in data_list:
            data_dict = {
                "vehicle_card": data.vehicle_card,
                "vehicle_type": VEHICLE_TYPE.get(2),
                "oil_type": data.oil_type,
                "driver_name": data.driver_name,
                "driver_id_card": data.driver_id_card,
                "driver_phone": data.driver_phone,
                "driver_sex": data.driver_sex,
                "driving_license_type": data.driving_license_type,
                "proprietor_name": data.proprietor_name,
                "proprietor_linkman": data.proprietor_linkman,
                "proprietor_link_phone": data.proprietor_link_phone,
                "proprietor_address": data.proprietor_address
            }
            vehicle_info_dict[data['vehicle_card']] = json_encode(data_dict)
        app_log.debug("Danger vehicle have {0} items will cache to redis".
                      format(len(vehicle_info_dict)))
        return vehicle_info_dict

    def get_all_taxi_info(self):
        """Get all taxi info used to cache to redis"""
        # TODO
        vehicle_info_dict = {}
        data_list = self.server.query(
            "SELECT "
            "v_ct_vd.vehicle_card AS vehicle_card, "  # 车牌号码
            "ct_voe.vehicleoiltype AS oil_type, "  # 燃油类型
            "pt_cr_ck.name AS driver_name, "  # 驾驶员姓名
            "pt_cr_ck.idcard AS driver_id_card, "  # 驾驶员身份证号
            "pt_cr_ck.mobilephone AS driver_phone,"  # 驾驶员联系方式
            "pt_cr_ck.gender AS driver_sex, "  # 驾驶员性别
            "pt_cr_ck.vehiclepermitted AS driving_license_type, "  # 驾照类型
            "et_pr.proprietorname AS proprietor_name,"  # 业户名称
            "et_pr.linkman AS proprietor_linkman,"  # 业户联系人
            "et_pr.linkphone AS proprietor_link_phone,"  # 业户联系电话
            "et_pr.address AS proprietor_address "  # 业户地址
            "FROM "
            "view_ct_vehicle_card AS v_ct_vd "
            "LEFT JOIN pt_careervehicle AS pt_ce "
            "ON v_ct_vd.id = pt_ce.vehicleid "
            "LEFT JOIN "

            "(SELECT pt_career.id,"
            "pt_career.name,"
            "pt_career.idcard,"
            "pt_career.mobilephone,"
            "pt_career.gender,"
            "pt_career.vehiclepermitted "
            "FROM pt_career "
            "LEFT JOIN pt_career_check   "
            "ON pt_career.id = pt_career_check.careerid) "
            "AS pt_cr_ck "

            "ON pt_ce.careerid = pt_cr_ck.id "
            "LEFT JOIN ct_vehicleoiltype AS ct_voe "
            "ON ct_voe.id = v_ct_vd.oiltypeid "
            "LEFT JOIN et_proprietor AS et_pr "
            "ON et_pr.id = v_ct_vd.proprietorbaseid "

            "WHERE v_ct_vd.vehiclepropertyid = 3"
        )
        for data in data_list:
            data_dict = {
                "vehicle_card": data.vehicle_card,
                "vehicle_type": VEHICLE_TYPE.get(3),
                "oil_type": data.oil_type,
                "driver_name": data.driver_name,
                "driver_id_card": data.driver_id_card,
                "driver_phone": data.driver_phone,
                "driver_sex": data.driver_sex,
                "driving_license_type": data.driving_license_type,
                "proprietor_name": data.proprietor_name,
                "proprietor_linkman": data.proprietor_linkman,
                "proprietor_link_phone": data.proprietor_link_phone,
                "proprietor_address": data.proprietor_address
            }
            vehicle_info_dict[data['vehicle_card']] = json_encode(data_dict)
        app_log.debug("Taxi have {0} items will cache to redis".
                      format(len(vehicle_info_dict)))
        return vehicle_info_dict

    def get_all_passenger_vehicle_info(self):
        """used to cache to redis"""
        # TODO
        vehicle_info_dict = {}
        data_list = self.server.query(
            "SELECT "
            "v_ct_vd.vehicle_card AS vehicle_card, "  # 车牌号码
            "ct_voe.vehicleoiltype AS oil_type, "  # 燃油类型
            "pt_cr_ck.name AS driver_name, "  # 驾驶员姓名
            "pt_cr_ck.idcard AS driver_id_card, "  # 驾驶员身份证号
            "pt_cr_ck.mobilephone AS driver_phone,"  # 驾驶员联系方式
            "pt_cr_ck.gender AS driver_sex, "  # 驾驶员性别
            "pt_cr_ck.vehiclepermitted AS driving_license_type, "  # 驾照类型
            "et_pr.proprietorname AS proprietor_name,"  # 业户名称
            "et_pr.linkman AS proprietor_linkman,"  # 业户联系人
            "et_pr.linkphone AS proprietor_link_phone,"  # 业户联系电话
            "et_pr.address AS proprietor_address "  # 业户地址
            "FROM "
            "view_ct_vehicle_card AS v_ct_vd "
            "LEFT JOIN pt_careervehicle AS pt_ce "
            "ON v_ct_vd.id = pt_ce.vehicleid "
            "LEFT JOIN "

            "(SELECT pt_career.id,"
            "pt_career.name,"
            "pt_career.idcard,"
            "pt_career.mobilephone,"
            "pt_career.gender,"
            "pt_career.vehiclepermitted "
            "FROM pt_career "
            "LEFT JOIN pt_career_check   "
            "ON pt_career.id = pt_career_check.careerid) "
            "AS pt_cr_ck "

            "ON pt_ce.careerid = pt_cr_ck.id "
            "LEFT JOIN ct_vehicleoiltype AS ct_voe "
            "ON ct_voe.id = v_ct_vd.oiltypeid "
            "LEFT JOIN et_proprietor AS et_pr "
            "ON et_pr.id = v_ct_vd.proprietorbaseid "

            "WHERE v_ct_vd.vehiclepropertyid = 4"
        )
        for data in data_list:
            data_dict = {
                "vehicle_card": data.vehicle_card,
                "vehicle_type": VEHICLE_TYPE.get(4),
                "oil_type": data.oil_type,
                "driver_name": data.driver_name,
                "driver_id_card": data.driver_id_card,
                "driver_phone": data.driver_phone,
                "driver_sex": data.driver_sex,
                "driving_license_type": data.driving_license_type,
                "proprietor_name": data.proprietor_name,
                "proprietor_linkman": data.proprietor_linkman,
                "proprietor_link_phone": data.proprietor_link_phone,
                "proprietor_address": data.proprietor_address
            }
            vehicle_info_dict[data['vehicle_card']] = json_encode(data_dict)
        app_log.debug("Passenger vehicle have {0} items will cache to redis".
                      format(len(vehicle_info_dict)))
        return vehicle_info_dict

    def get_all_tourist_vehicle_info(self):
        """used to cache to redis"""
        # TODO
        vehicle_info_dict = {}
        data_list = self.server.query(
            "SELECT "
            "v_ct_vd.vehicle_card AS vehicle_card, "  # 车牌号码
            "v_ct_vd.vehiclepropertyid AS vehicle_type_id, "  # 车辆类型ID
            "ct_voe.vehicleoiltype AS oil_type, "  # 燃油类型
            "pt_cr_ck.name AS driver_name, "  # 驾驶员姓名
            "pt_cr_ck.idcard AS driver_id_card, "  # 驾驶员身份证号
            "pt_cr_ck.mobilephone AS driver_phone,"  # 驾驶员联系方式
            "pt_cr_ck.gender AS driver_sex, "  # 驾驶员性别
            "pt_cr_ck.vehiclepermitted AS driving_license_type, "  # 驾照类型
            "et_pr.proprietorname AS proprietor_name,"  # 业户名称
            "et_pr.linkman AS proprietor_linkman,"  # 业户联系人
            "et_pr.linkphone AS proprietor_link_phone,"  # 业户联系电话
            "et_pr.address AS proprietor_address "  # 业户地址
            "FROM "
            "view_ct_vehicle_card AS v_ct_vd "
            "LEFT JOIN pt_careervehicle AS pt_ce "
            "ON v_ct_vd.id = pt_ce.vehicleid "
            "LEFT JOIN "

            "(SELECT pt_career.id,"
            "pt_career.name,"
            "pt_career.idcard,"
            "pt_career.mobilephone,"
            "pt_career.gender,"
            "pt_career.vehiclepermitted "
            "FROM pt_career "
            "LEFT JOIN pt_career_check   "
            "ON pt_career.id = pt_career_check.careerid) "
            "AS pt_cr_ck "

            "ON pt_ce.careerid = pt_cr_ck.id "
            "LEFT JOIN ct_vehicleoiltype AS ct_voe "
            "ON ct_voe.id = v_ct_vd.oiltypeid "
            "LEFT JOIN et_proprietor AS et_pr "
            "ON et_pr.id = v_ct_vd.proprietorbaseid "

            "WHERE v_ct_vd.vehiclepropertyid = 5"
        )
        for data in data_list:
            data_dict = {
                "vehicle_card": data.vehicle_card,
                "vehicle_type": VEHICLE_TYPE.get(data.vehicle_type_id),
                "oil_type": data.oil_type,
                "driver_name": data.driver_name,
                "driver_id_card": data.driver_id_card,
                "driver_phone": data.driver_phone,
                "driver_sex": data.driver_sex,
                "driving_license_type": data.driving_license_type,
                "proprietor_name": data.proprietor_name,
                "proprietor_linkman": data.proprietor_linkman,
                "proprietor_link_phone": data.proprietor_link_phone,
                "proprietor_address": data.proprietor_address
            }
            vehicle_info_dict[data['vehicle_card']] = json_encode(data_dict)
        app_log.debug("Tourist vehicle have {0} items will cache to redis".
                      format(len(vehicle_info_dict)))
        return vehicle_info_dict

    def get_all_law_people_info(self):
        # TODO
        pass

    def get_all_law_vehicle_info(self):
        # TODO
        pass

    def get_vehicle_type_by_card(self, vehicle_card):
        """
        Get a vehicle's type by vehicle_card
        :return: vehicle type str or None
        """
        vehicle_type = self.server.query(
            "SELECT vehiclepropertyid "
            "FROM "
            "view_ct_vehicle_card "
            "WHERE vehicle_card = %s ", vehicle_card
        )

        if vehicle_type:
            type_id = vehicle_type[0].vehiclepropertyid
            return VEHICLE_TYPE[type_id]

    def get_need_remove_vehicle(self):
        """
        Get vehicle card list which did not update location in five minutes.
        :return:
        """
        # XXX: ioloop blocking > 0.5 use queries or run in a thread.
        # this place need improve
        type_2_dict = {"type": VEHICLE_TYPE.get(2), "action": "delete", "data": []}
        type_3_dict = {"type": VEHICLE_TYPE.get(3), "action": "delete", "data": []}
        type_4_dict = {"type": VEHICLE_TYPE.get(4), "action": "delete", "data": []}
        type_5_dict = {"type": VEHICLE_TYPE.get(5), "action": "delete", "data": []}
        type_7_dict = {"type": VEHICLE_TYPE.get(7), "action": "delete", "data": []}

        now_time = datetime.datetime.now()
        time_obj = now_time - datetime.timedelta(seconds=VEHICLE_EXPIRE_SECOND)
        time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
        item_list = self.server.query(
            "SELECT "
            "dt_vs.vehicle_card,"
            "v_ct_vd.vehiclepropertyid AS type_id "
            "FROM   dt_vehiclegps AS dt_vs "
            "LEFT JOIN view_ct_vehicle_card AS v_ct_vd "
            "ON dt_vs.vehicle_card = v_ct_vd.vehicle_card "
            "WHERE dt_vs.last_update_time < %s", time_str
        )
        for item in item_list:
            if item["type_id"] == 2:
                type_2_dict["data"].append(item["vehicle_card"])
            elif item["type_id"] == 3:
                type_3_dict["data"].append(item["vehicle_card"])
            elif item["type_id"] == 4:
                type_4_dict["data"].append(item["vehicle_card"])
            elif item["type_id"] == 5:
                type_5_dict["data"].append(item["vehicle_card"])
            elif item["type_id"] == 7:
                type_7_dict["data"].append(item["vehicle_card"])
            else:
                pass
        return [
            type_2_dict,
            type_3_dict,
            type_4_dict,
            type_5_dict,
            type_7_dict
        ]

publish_message_cache_model = PublishMessageCacheModel()
