# -*- coding:utf-8 -*- 
# --------------------
# Author:		gxm1015@qq.com
# Description:	消息实时推送及缓存相关操作.
# Time: 2017-1-18
# --------------------

from tornado.escape import json_encode, json_decode
from tornado.log import app_log

from config import (GPS_QUEUE_KEY, VEHICLE_TYPE_GPS_KEY,
                   VEHICLE_LOADED_KEY, CLIENT_STATE_KEY,
                   DANGER_FREIGHT_VEHICLE_INFO_CACHE,
                   PASSENGER_VEHICLE_INFO_CACHE,
                   TOURIST_VEHICLE_INFO_CACHE,
                   TAXI_INFO_CACHE,
                   LAW_PEOPLE_INFO_CACHE,
                   LAW_VEHICLE_INFO_CACHE,
                   ALL_VEHICLE_INFO_CACHE)
from db.dbManager import rsdb
from ..utils.coordTransform import wgs84_to_bd09
from ..model.PublishMessageCacheModel import publish_message_cache_model


class VehicleGpsQueue(object):
    """
    Vehicle real time gps message FIFO queue.
    """

    def __init__(self, server, key):
        """
        Initialize redis queue.
        :param server: redis connection
        :param key: key for this queue
        """
        self.server = server
        self.key = key

    def push(self, gps_msg_json):
        """Push a gps message"""
        self.server.lpush(self.key, gps_msg_json)

    def pop(self, timeout=0):
        """Pop a gps message"""
        if timeout > 0:
            data = self.server.brpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.rpop(self.key)
        if data:
            return data

    def clear(self):
        """Clear queue"""
        self.server.delete(self.key)

    def __len__(self):
        """Return the length of the queue"""
        return self.server.llen(self.key)


gps_queue_instance = VehicleGpsQueue(rsdb, GPS_QUEUE_KEY)


class LCICCache(object):
    """
    Some Cache operation before LCIC START.
    Some method get information from redis cache.
    """

    def __init__(self, server):
        """
        Initialize vehicle's gps info cache.
        :param server: redis connection
        """
        self.server = server
        self.vehicle_type_key = VEHICLE_TYPE_GPS_KEY
        self.danger_key = DANGER_FREIGHT_VEHICLE_INFO_CACHE
        self.passenger_key = PASSENGER_VEHICLE_INFO_CACHE
        self.tourist_key = TOURIST_VEHICLE_INFO_CACHE
        self.taxi_key = TAXI_INFO_CACHE
        self.law_people_key = LAW_PEOPLE_INFO_CACHE
        self.law_vehicle_key = LAW_VEHICLE_INFO_CACHE

    def flush_all_lcic_redis_key(self):
        """
        Call this method before cache_vehicle_type_gps info.
        Flush all redis key which start with lcic.
        """
        # XXX:keys() O(n)
        lcic_key_list = self.server.keys('lcic*')
        if lcic_key_list:
            app_log.debug('Flush all LCIC redis key')
            self.server.delete(*lcic_key_list)

    def cache_all_vehicle_info(self):
        app_log.debug('Cache vehicle info to redis...')
        vehicle_info_dict = publish_message_cache_model.get_all_vehicle_info()
        self.server.hmset(
            ALL_VEHICLE_INFO_CACHE,
            vehicle_info_dict
        )

    def cache_danger_freight_vehicle_info(self):
        """Cache all danger freight vehicle info to redis"""
        vehicle_info_dict = publish_message_cache_model.get_all_danger_freight_vehicle_info()
        self.server.hmset(
            self.danger_key,
            vehicle_info_dict
        )
        app_log.info('Danger freight vehicle Cached.')

    def cache_taxi_info(self):
        """Cache all taxi info to redis"""
        vehicle_info_dict = publish_message_cache_model.get_all_taxi_info()
        self.server.hmset(
            self.taxi_key,
            vehicle_info_dict
        )
        app_log.info('Taxi info Cached.')

    def cache_passenger_vehicle_info(self):
        """Cache all passenger vehicle info to redis"""
        vehicle_info_dict = publish_message_cache_model.get_all_passenger_vehicle_info()
        self.server.hmset(
            self.passenger_key,
            vehicle_info_dict
        )
        app_log.info('Passenger vehicle info Cached.')

    def cache_tourist_vehicle_info(self):
        """Cache all tourist vehicle info to redis"""
        vehicle_info_dict = publish_message_cache_model.get_all_tourist_vehicle_info()
        self.server.hmset(
            self.tourist_key,
            vehicle_info_dict
        )
        app_log.info('Tourist vehicle info Cached.')

    def cache_law_people_info(self):
        """Cache all law people info to redis"""
        people_info_dict = publish_message_cache_model.get_all_law_people_info()
        self.server.hmset(
            self.law_people_key,
            people_info_dict
        )
        app_log.info('Law people info Cached.')

    def cache_law_vehicle_info(self):
        """Cache all law vehicle info to redis"""
        vehicle_info_dict = publish_message_cache_model.get_all_law_vehicle_info()
        self.server.hmset(
            self.law_vehicle_key,
            vehicle_info_dict
        )
        app_log.info('Law vehicle info Cached.')

    def cache_vehicle_type_gps(self):
        """Cache all Vehicle's gps info, type as a json to redis."""
        vehicle_info_dict = publish_message_cache_model.get_all_vehicle_type_gps_info()
        self.server.hmset(
            self.vehicle_type_key,
            vehicle_info_dict
        )
        app_log.info('Vehicle type map Cached.')

    def lcic_start_cache(self):
        """
        Before LCIC start cache info to redis.
        :return:
        """
        self.flush_all_lcic_redis_key()
        self.cache_all_vehicle_info()
        # self.cache_danger_freight_vehicle_info()
        # self.cache_passenger_vehicle_info()
        # self.cache_tourist_vehicle_info()
        # self.cache_taxi_info()
        # self.cache_law_people_info()
        # self.cache_law_vehicle_info()
        self.cache_vehicle_type_gps()
        app_log.info('All Cached successful.')

    def reload_lcic_info_cache(self):
        """
        After postgres data synchronized,
        Call this method do reload cache information.
        :return:
        """
        need_flushed_key = [
            VEHICLE_TYPE_GPS_KEY,
            DANGER_FREIGHT_VEHICLE_INFO_CACHE,
            TAXI_INFO_CACHE,
            PASSENGER_VEHICLE_INFO_CACHE,
            TOURIST_VEHICLE_INFO_CACHE,
            LAW_VEHICLE_INFO_CACHE,
            LAW_PEOPLE_INFO_CACHE
        ]
        app_log.debug('Flush need reload redis key:{0}'.format(need_flushed_key))
        self.server.delete(*need_flushed_key)
        self.cache_danger_freight_vehicle_info()
        self.cache_passenger_vehicle_info()
        self.cache_tourist_vehicle_info()
        self.cache_taxi_info()
        # self.cache_law_people_info()
        # self.cache_law_vehicle_info()
        self.cache_vehicle_type_gps()
        app_log.info('Reload successful.')

    def get_danger_freight_vehicle_info(self, vehicle_card):
        return self.server.hget(self.danger_key, vehicle_card)

    def get_taxi_info(self, vehicle_card):
        return self.server.hget(self.taxi_key, vehicle_card)

    def get_passenger_vehicle_info(self, vehicle_card):
        return self.server.hget(self.passenger_key, vehicle_card)

    def get_tourist_vehicle_info(self, vehicle_card):
        return self.server.hget(self.tourist_key, vehicle_card)

    def get_law_people_info(self, people_id):
        return self.server.hget(self.law_people_key, people_id)

    def get_law_vehicle_info(self, vehicle_card):
        return self.server.hget(self.law_vehicle_key, vehicle_card)

    def update_vehicle_type_gps(self, gps_info_json):
        """
        Update a vehicle's gps info.
        vehicle type contains in old_gps_info_json.
        :return: a vehicle info contains type, gps info or None
        """
        gps_info_dict = json_decode(gps_info_json)
        vehicle_card = gps_info_dict["data"]["vehicle_card"].encode('utf-8')
        old_gps_info_json = self.server.hget(
            self.vehicle_type_key,
            vehicle_card
        )
        if old_gps_info_json:
            old_gps_info_dict = json_decode(old_gps_info_json)
            bd09_pt = wgs84_to_bd09(
                [(gps_info_dict["data"]["lng"], gps_info_dict["data"]["lat"])]
            )
            old_gps_info_dict.update(
                data=gps_info_dict["data"],
                lng=bd09_pt[0],
                lat=bd09_pt[1]
            )
            self.server.hset(
                self.vehicle_type_key,
                vehicle_card,
                json_encode(old_gps_info_dict)
            )
            return old_gps_info_dict

    def get_vehicle_type_gps_by_card(self, vehicle_card):
        """
        Get a vehicle's type, gps info by vehicle_card.
        :param vehicle_card:
        :return: a json contains vehicle's type, gps info or 0.
        """
        return self.server.hget(self.vehicle_type_key, vehicle_card)

    def add_vehicle_type_gps(self, gps_info_json):
        """
        Add a vehicle info to redis cache that info contains vehicle type, gps info.
        :param gps_info_json:
        :return:
        """
        new_gps_info_json = ''
        gps_info_dict = json_decode(gps_info_json)
        vehicle_card = gps_info_dict["data"]["vehicle_card"]
        if not gps_info_dict["type"]:
            vehicle_type_str = publish_message_cache_model.get_vehicle_type_by_card(vehicle_card)
            if vehicle_type_str:
                gps_info_dict.update(type=vehicle_type_str)
                new_gps_info_json = json_encode(gps_info_dict)
            else:
                app_log.warn("Did not find {0}'s type".format(vehicle_card))
                return
        self.server.hset(self.vehicle_type_key, vehicle_card, new_gps_info_json)

    # get_vehicle_by_json() return a dict new_gps_info_json or None.
    get_vehicle_by_json = update_vehicle_type_gps


lcic_cache_instance = LCICCache(rsdb)


class ClientStateCache(object):
    """
        客户端状态管理缓存.
    """

    def __init__(self, server, key):
        """
        :param server: redis connection
        :param key: redis key name
        """
        self.server = server
        self.key = key

    def set_client_state(self, session_id, state_json):
        """
        After sock js received client state msg(msg_type="client_state"),
        cache it to redis
        :session_id: sock js session_id
        :state_json:
        {
            "msg_type":"client_state",
            "session_id": session_id,
            "type": a array. [value in VEHICLE_TYPE dict],
            "rectangle_pt": [{"lng":lng, "lat": lat},{},{},{}]
        }
        """
        self.server.hset(self.key, session_id, state_json)

    def get_client_state_by_session_id(self, session_id):
        """Return client's state_json by session_id"""
        return self.server.hget(self.key, session_id)

    def get_all_client_state(self):
        """
        :return: a list contains all client's state_json.
        """
        state_key_list = self.server.hkeys(self.key)
        return [self.get_client_state_by_session_id(session_id) for session_id in state_key_list]

    def clear_client_state(self, session_id):
        """
        After a sock js connection closed,
        clear the client's state_json
        """
        self.server.hdel(self.key, session_id)


client_state_cache_instance = ClientStateCache(rsdb, CLIENT_STATE_KEY)


class ClientLoadedVehicleCache(object):
    """
        相应客户端已加载车辆缓存.
    """
    key = VEHICLE_LOADED_KEY

    @classmethod
    def set_vehicle_loaded(cls, session_id, type_id, vehicle_card_data):
        """
        Cache all client loaded vehicle card to redis
        :param session_id: client's session id.
        :param type_id: vehicle's type_id
        :param vehicle_card_data:
        {"vehicle_card": vehicle_card, ...} or a vehicle_card str
        """
        key = cls.key + session_id + ":" + type_id
        if vehicle_card_data:
            if isinstance(vehicle_card_data, dict):
                rsdb.hmset(key, vehicle_card_data)
            else:
                # XXX: check vehicle_card_data type.
                rsdb.hset(key, vehicle_card_data, vehicle_card_data)

    @classmethod
    def remove_type_loaded(cls, session_id, type_id):
        """
        After a client unchecked a type which type's id equals type_id.
        remove this type's redis key.
        :param session_id:
        :param type_id:
        :return:
        """
        key = cls.key + session_id + ":" + type_id
        rsdb.delete(key)

    @classmethod
    def remove_vehicle_loaded(cls, session_id, type_id, vehicle_card_data):
        """
        remove the vehicle_card from loaded cache.
        :param session_id
        :param type_id: vehicle type id
        :param vehicle_card_data: a list contains vehicle_card or a vehicle_card str.
        :return:
        """
        key = cls.key + session_id + ":" + type_id
        if isinstance(vehicle_card_data, list):
            rsdb.hdel(key, *vehicle_card_data)
        else:
            rsdb.hdel(key, vehicle_card_data)

    @classmethod
    def get_loaded_cache_key_by_session(cls, session_id):
        key = VEHICLE_LOADED_KEY + session_id + "*"
        return rsdb.keys(key)

    @classmethod
    def add_vehicle(cls, session_id, type_id, vehicle_card):
        """
        Add a vehicle_card to cache
        :vehicle_card: vehicle_card
        :session_id: client's session_id
        """
        key = cls.key + session_id + ":" + type_id
        rsdb.hset(key, vehicle_card, vehicle_card)

    @classmethod
    def is_vehicle_loaded(cls, session_id, type_id, vehicle_card):
        """
        根据session_id 判断当前客户端是否已加载过此车辆.
        :param vehicle_card:
        :param type_id:
        :param session_id:
        :return:
        """
        key = cls.key + session_id + ":" + type_id
        if rsdb.exists(key):
            return rsdb.hexists(key, vehicle_card)
        else:
            return False

    @staticmethod
    def clear_vehicle_loaded(session_id):
        """
        After a sock js connection closed,
        clear the loaded vehicle_card.
        """
        keys = rsdb.keys(VEHICLE_LOADED_KEY + session_id + "*")
        if keys:
            rsdb.delete(*keys)

    @staticmethod
    def get_all_loaded_cache_key():
        """Return all VEHICLE_LOADED_KEY Cache key."""
        # XXX: keys O(n) NOT USEFUL
        return rsdb.keys(VEHICLE_LOADED_KEY + '*')

    @staticmethod
    def vehicle_card_loaded_key_list(vehicle_card, type_id):
        """
        If vehicle_card in redis cache.
        return client's session_id which client loaded.
        """
        # XXX: NOT USEFUL
        loaded_client_key_list = []
        for key in ClientLoadedVehicleCache.get_all_loaded_cache_key():
            if key[-1] == str(type_id):
                if rsdb.hexists(key, vehicle_card):
                    loaded_client_key_list.append(key)
        return loaded_client_key_list
