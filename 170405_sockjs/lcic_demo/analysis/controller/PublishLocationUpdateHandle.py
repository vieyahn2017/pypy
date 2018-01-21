# -*- coding:utf-8 -*- 
# --------------------
# Author:		gxm1015@qq.com
# Description:	信息实时推送外理 Use SockJS or Tornado long polling.
# --------------------
import tornado.ioloop
import functools
from sockjs.tornado import SockJSConnection
from tornado import gen
from tornado.concurrent import Future
from tornado.escape import json_decode, json_encode
from tornado.web import RequestHandler
from tornado.log import app_log

from config import VEHICLE_TYPE, VEHICLE_EXPIRE_SECOND, VEHICLE_TYPE_REVERSE
from .PublishMessageCache import (client_state_cache_instance,
                                  ClientLoadedVehicleCache)
from ..model.PublishMessageCacheModel import publish_message_cache_model


class LocationRealTimeUpdateHandler(SockJSConnection):
    """Sock Connection"""
    clients = set()
    remove_vehicle_running = False

    def on_open(self, info):
        # XXX: need improve.
        # if not LocationRealTimeUpdateHandler.remove_vehicle_running:
        #     self._run_send_remove_vehicle()
        #     LocationRealTimeUpdateHandler.remove_vehicle_running = True
        self.clients.add(self)

    def on_message(self, msg_json):
        """
        Now only one msg_type(client_state info) received from client.
        :param msg_json:
        :return:
        """
        msg_dict = json_decode(msg_json)
        try:
            if msg_dict["msg_type"] == "client_state":
                old_state = client_state_cache_instance.get_client_state_by_session_id(
                    self.session.session_id
                )
                if old_state:
                    old_state_dict = json_decode(old_state)
                    loaded_types = set(old_state_dict["types"])
                    now_types = set(msg_dict["types"])
                    need_clear_type = loaded_types.difference(now_types)
                    if need_clear_type:
                        for type_str in need_clear_type:
                            if VEHICLE_TYPE_REVERSE.get(type_str):
                                ClientLoadedVehicleCache.remove_type_loaded(
                                    self.session.session_id,
                                    VEHICLE_TYPE_REVERSE.get(type_str)
                                )

                client_state_cache_instance.set_client_state(
                    self.session.session_id,
                    msg_json
                )
        except KeyError as e:
            app_log.warn(e)

    def on_close(self):
        """
        After a sock js connection closed,
        clear this session's client state from redis.
        :return:
        """
        app_log.debug('Sock JS closed!')
        client_state_cache_instance.clear_client_state(self.session.session_id)
        ClientLoadedVehicleCache.clear_vehicle_loaded(self.session.session_id)

        self.clients.remove(self)

    def publish(self, msg_body):
        self.broadcast(self.clients, msg_body)

    @classmethod
    def msg_send_handler(cls, msg_dict):
        """
        Send vehicle info to client.
        :param msg_dict: a dict contains vehicle_type, gps info, vehicle info
        :return:
        """
        need_push_session_id_list = []
        client_state_json_list = client_state_cache_instance.get_all_client_state()
        if client_state_json_list:
            need_push_session_id_list = LocationRealTimeUpdateHandler._get_need_push_session_id(
                    msg_dict,
                    client_state_json_list
                )
        if need_push_session_id_list:
            cls._do_push_msg(msg_dict, need_push_session_id_list)

    @classmethod
    def send_need_remove_vehicle(cls):
        """
        Send need remove vehicle card to client every ten minutes.
        send data format: {"action": "delete", "type": vehicle_type,"data":[vehicle_card, vehicle_card...]}
        """
        client_load_vehicle_type_dict = {}
        data_list = publish_message_cache_model.get_need_remove_vehicle()
        client_state_json_list = client_state_cache_instance.get_all_client_state()

        if client_state_json_list:
            client_state_dict_list = \
                [json_decode(state_json) for state_json in client_state_json_list]
            for client_state in client_state_dict_list:
                if client_state["types"]:
                    client_load_vehicle_type_dict[client_state["session_id"]] = \
                        client_state["types"]

        if client_load_vehicle_type_dict:
            for client in cls.clients:
                session_id = client.session.session_id
                if session_id in client_load_vehicle_type_dict:
                    types = client_load_vehicle_type_dict[session_id]
                    for data in data_list:
                        if data["data"] and (data["type"] in types):
                            app_log.debug('send need remove vehicle type:{0}, length:{1}'.
                                          format(data['type'], len(data['data'])))
                            # remove vehicle card from client loaded cache
                            # ClientLoadedVehicleCache.remove_vehicle_loaded(
                            #     session_id,
                            #     VEHICLE_TYPE_REVERSE.get(data["type"]),
                            #     data["data"]
                            # )
                            client.send(json_encode(data))

    @staticmethod
    def _get_need_push_session_id(msg_dict, client_state_json_list):
        session_id_list = []
        vehicle_type = msg_dict["type"]

        client_state_dict_list = [json_decode(state_json) for state_json in client_state_json_list]
        for client_state in client_state_dict_list:
            if vehicle_type in client_state["types"]:
                session_id_list.append(client_state["session_id"])

        return session_id_list

    @classmethod
    def _do_push_msg(cls, msg_dict, need_push_session_id_list):
        vehicle_card = msg_dict["data"]["vehicle_card"]
        vehicle_type = msg_dict["type"]

        for client in cls.clients:
            client_session_id = client.session.session_id
            if client_session_id in need_push_session_id_list:
                is_loaded = ClientLoadedVehicleCache.is_vehicle_loaded(
                    client_session_id,
                    VEHICLE_TYPE_REVERSE.get(vehicle_type),
                    vehicle_card
                )
                if is_loaded:
                    client.send(json_encode(msg_dict))
                else:
                    app_log.debug(u"Client not loaded: {0}".format(vehicle_card))
                    # TODO:
                    msg_dict.update(action="insert")
                    client.send(json_encode(msg_dict))
                    ClientLoadedVehicleCache.add_vehicle(
                        client_session_id,
                        VEHICLE_TYPE_REVERSE.get(vehicle_type),
                        vehicle_card
                    )

                    if vehicle_type == VEHICLE_TYPE.get(1):
                        pass
                    elif vehicle_type == VEHICLE_TYPE.get(2):
                        pass
                    elif vehicle_type == VEHICLE_TYPE.get(3):
                        pass
                    elif vehicle_type == VEHICLE_TYPE.get(4):
                        pass
                    elif vehicle_type == VEHICLE_TYPE.get(5):
                        pass
                    elif vehicle_type == VEHICLE_TYPE.get(6):
                        pass
                    elif vehicle_type == VEHICLE_TYPE.get(7):
                        pass

    @classmethod
    def pub_sub(cls, data):
        for client in cls.clients:
            client.send(data)

    def _run_send_remove_vehicle(self):
        periodic_callback = tornado.ioloop.PeriodicCallback(
            functools.partial(LocationRealTimeUpdateHandler.send_need_remove_vehicle),
            1000 * VEHICLE_EXPIRE_SECOND
        )
        periodic_callback.start()


class MessageBuffer(object):
    """Long polling message buffer"""

    def __init__(self):
        self.clients = set()
        self.cache = []
        self.cache_size = 20

    def wait_for_message(self, cursor=None):
        result_future = Future()
        if cursor:
            new_count = 0
            for msg in reversed(self.cache):
                if msg["id"] == cursor:
                    break
                new_count += 1
            if new_count:
                result_future.set_result(self.cache[-new_count:])
                return result_future
        self.clients.add(result_future)
        return result_future

    def cancel_wait(self, future):
        self.clients.remove(future)
        future.set_result([])

    def new_messages(self, messages):
        """
        :param messages:
        :return:
        """
        for future in self.clients:
            future.set_result(messages)
        self.clients = set()
        self.cache.extend(messages)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size:]


global_message_buffer = MessageBuffer()


class LongPollingUpdaterHandler(RequestHandler):
    @gen.coroutine
    def post(self):
        cursor = self.get_argument("cursor", None)
        self.future = global_message_buffer.wait_for_message(cursor)
        messages = yield self.future
        if self.request.connection.stream.closed():
            return
        self.write(dict(messages=messages))

    def on_connection_close(self):
        global_message_buffer.cancel_wait(self.future)

