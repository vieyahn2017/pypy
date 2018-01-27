# -*- coding: utf-8 -*-
# --------------------
# Description:	坐标转换相关函数.
# --------------------
import json
import math

import requests
from requests.exceptions import HTTPError

key = '74cae1499abd8a561b10862c7a492c8e'  # 这里填写你的高德api的key
bd_key = 'q9ZhAMejH5Ho5488shqPj2kqM4EFn13c'  # 百度KEY
bd_sn = 'hsjn42dl0ALmyXVx0khIRhEM5n5WwPMr'  # 百度SN KEY
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率


def geocode(address):
    """
    利用高德geocode服务解析地址获取位置坐标
    :param address:需要解析的地址
    :return:
    """
    geocoding = {'s': 'rsv3',
                 'key': key,
                 'city': '全国',
                 'address': address}
    res = requests.get(
        "http://restapi.amap.com/v3/geocode/geo", params=geocoding)
    if res.status_code == 200:
        res_json = res.json()
        status = res_json.get('status')
        count = res_json.get('count')
        if status == '1' and int(count) >= 1:
            geocodes = res_json.get('geocodes')[0]
            lng = float(geocodes.get('location').split(',')[0])
            lat = float(geocodes.get('location').split(',')[1])
            return lng, lat
        else:
            return None
    else:
        return None


def wgs84_to_gcj02_use_amp_api(pt_list):
    """
    WGS84 转 GCJ02 使用高德提供的API
    :pt_list: a list. [(lng, lat),(lng, lat),(lng, lat)...] or [lng, lat]
    :return lng, lat
    """
    pt_gcj02_result = []

    if not isinstance(pt_list, list):
        raise TypeError
    if len(pt_list) == 0:
        raise ValueError

    if len(pt_list) == 1:
        lng, lat = pt_list[0], pt_list[1]
        request_url = "http://restapi.amap.com/v3/assistant/coordinate/convert" \
                      "?locations={0},{1}&coordsys=gps&output=json&key={2}".format(lng, lat, key)
        try:
            res = requests.get(request_url)
            pt = json.loads(res.content)
            if pt['status'] == 1:
                pt_gcj02_result = [float(p) for p in pt['locations'].split(',')]
        except HTTPError as e:
            print(e)
    else:
        pt_str = ''
        for pt in pt_list:
            temp = str(pt[0]) + ',' + str(pt[1]) + ';'
            pt_str += temp
        request_url = "http://restapi.amap.com/v3/assistant/coordinate/convert" \
                      "?locations={0}&coordsys=gps&output=json&key={1}".format(pt_str, key)

        try:
            res = requests.get(request_url)
            pt = json.loads(res.content)
            if int(pt['status']) == 1:
                result = [p.split(',') for p in pt['locations'].split(';')]
                for pt in result:
                    lng, lat = round(float(pt[0]), 6), round(float(pt[1]), 6)
                    pt_gcj02_result.append((lng, lat))
        except HTTPError as e:
            print(e)

    return pt_gcj02_result


def wgs84_to_gcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return lng, lat
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return mglng, mglat


def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return bd_lng, bd_lat


def wgs84_to_bd09(pt_list):
    """
    wgs84 to bd09
    :param pt_list:[(lng, lat),...]
    :return: bd09 point list , if only on point return a point tuple
    """
    result_list = []
    if not isinstance(pt_list, list):
        raise TypeError('need a list.')

    if len(pt_list) >= 1:
        for pt in pt_list:
            lng, lat = pt[0], pt[1]
            lng_02, lat_02 = wgs84_to_gcj02(lng, lat)
            lng_09, lat_09 = gcj02_to_bd09(lng_02, lat_02)
            result_list.append((round(lng_09, 6), round(lat_09, 6)))
    if len(result_list) == 1:
        return result_list[0]
    else:
        return result_list


def bd09_to_wgs84(pt_list):
    """
    bd09 to wgs84
    :param pt_list:[(lng, lat),...]
    :return: a point tuple list. if only on point return a point tuple
    """
    result_list = []
    if not isinstance(pt_list, list):
        raise TypeError('need a list')

    if len(pt_list) >= 1:
        for pt in pt_list:
            lng, lat = pt[0], pt[1]
            lng_02, lat_02 = bd09_to_gcj02(lng, lat)
            lng_84, lat_84 = gcj02_to_wgs84(lng_02, lat_02)
            result_list.append((round(lng_84, 6), round(lat_84, 6)))
    if len(result_list) == 1:
        return result_list[0]
    else:
        return result_list


def wgs84_to_bd09_use_api(pt_list):
    """
    使用百度API将wgs84 坐标转为 百度坐标, 批量转换最多支持100个点.
    :pt_list: a list. [(lng, lat),(lng, lat),(lng, lat)...]
    :return:bd09 point list
    """
    pt_bd09_result = []

    if not isinstance(pt_list, list):
        raise TypeError
    pt_list_len = len(pt_list)
    if pt_list_len == 0 or pt_list_len > 100:
        raise ValueError

    if len(pt_list) == 1:
        lng, lat = pt_list[0], pt_list[1]
        request_url = "http://api.map.baidu.com/geoconv/v1/" \
                      "?coords={0},{1}&from=1&to=5&&ak={2}".format(lng, lat, bd_key)
        try:
            res = requests.get(request_url)
            pt = json.loads(res.content)
            if pt['status'] == 0:
                pt_bd09_result = [float(p) for p in pt['locations'].split(',')]
        except HTTPError as e:
            print(e)
    else:
        pt_str = ''
        for pt in pt_list:
            temp = str(pt[0]) + ',' + str(pt[1]) + ';'
            pt_str += temp
        pt_str = pt_str[:-1]
        request_url = "http://api.map.baidu.com/geoconv/v1/" \
                      "?coords={0}&from=1&to=5&ak={1}".format(pt_str, bd_key)

        try:
            res = requests.get(request_url)
            pt = json.loads(res.content)
            if pt['status'] == 0:
                result = [(p['x'], p['y']) for p in pt['result']]
                for pt in result:
                    lng, lat = round(float(pt[0]), 6), round(float(pt[1]), 6)
                    pt_bd09_result.append((lng, lat))
        except HTTPError as e:
            print(e)

    return pt_bd09_result


def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return gg_lng, gg_lat


def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return lng, lat
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return lng * 2 - mglng, lat * 2 - mglat


def transform_lat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def transform_lng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)


if __name__ == '__main__':
    print(wgs84_to_gcj02(106.575355, 26.597229))
    print(wgs84_to_gcj02_use_amp_api([(106.575355, 26.597229), (106.575355, 26.597229)]))
    print(wgs84_to_bd09_use_api([(106.575355, 26.597229), (106.575355, 26.597229)]))
