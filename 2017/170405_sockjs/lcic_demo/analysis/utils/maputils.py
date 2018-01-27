# -*- coding:utf-8 -*- 
# --------------------
# Author:		Ken
# Description:	地理信息工具库
# --------------------

from math import radians, cos, sin, asin, sqrt


# 电子围栏，判断是否在多边形内
def is_pt_in_poly(Alon, Alat, Apoints):
    """
    :param Alon: lng
    :param Alat: lat
    :param Apoints: [{'lng':lng, 'lat':lat},{'lng':lng, 'lat':lat},...]
    :return:
    """
    # TODO: Change Apoints format to [(lng, lat),(lng, lat),(lng, lat)...]
    iSum = 0
    if not Apoints or len(Apoints) < 3:
        return False
    for index, point in enumerate(Apoints):
        dLon1 = point['lng']
        dLat1 = point['lat']
        if index == len(Apoints) - 1:
            dLon2 = Apoints[0]['lng']
            dLat2 = Apoints[0]['lat']
        else:
            dLon2 = Apoints[index + 1]['lng']
            dLat2 = Apoints[index + 1]['lat']
        if (Alat >= dLat1 and Alat < dLat2) or (Alat >= dLat2 and Alat < dLat1):
            if abs(dLat1 - dLat2) > 0:
                dLon = dLon1 - ((dLon1 - dLon2) * (dLat1 - Alat)) / (dLat1 - dLat2)
                if dLon < Alon:
                    iSum += 1
    if iSum % 2 != 0:
        return True
    return False


# 计算两个经纬度间的距离
def get_distance(lon1, lat1, lon2, lat2):  # 经度1，纬度1，经度2，纬度2 （十进制度数）
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球平均半径，单位为公里
    return c * r * 1000
