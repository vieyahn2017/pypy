# -*- coding: utf-8 -*-
import requests
requests.packages.urllib3.disable_warnings()
import gevent
from gevent import monkey
monkey.patch_all()


def fetch(url):
    result = {}
    try :
        response = requests.get(url=url, verify=False)
        result = response.json()
        print result
    except Exception, e:
        print e
    return result

def asynchronous():
    url = "https://127.0.0.1:8088/deviceManager/v1/rest/1270000000018088/replicationpair"
    fetch_one = gevent.spawn(fetch, url)
    fetch_one.join()
    # gevent.joinall([fetch_one])
    return fetch_one.value
