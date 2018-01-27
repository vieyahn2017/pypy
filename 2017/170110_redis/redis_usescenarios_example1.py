#!/usr/bin/env python
# coding=utf-8

#应用场景 – 实时用户统计

import time
from redis import redis
from datetime import datetime
ONLINE_LASAT_MINUTES = 5
redis = Redis()

def mark_online(user_id):
    now = int(time.time())
    expires = now + (app.config[ONLINE_LASAT_MINUTES] *60) +10
    all_users_key = 'online-users/%d' % (now // 60)
    user_key = 'user-activity' % user_id
    p = redis.pipeline()
    p.sadd(all_users_key, user_id)
    p.set(user_key, now)
    p.expireat(all_users_key, expires)
    p.expireat(user_key, expires)
    p.execute()

def get_user_last_activity(user_id)    :
    last_active = redis.get('user-activity/%s' % user_id)
    if last_active is None:
        return None
    return datetime.utcfromtimestamp(int(last_active))

def get_online_users():
    current = int(time.time()) // 60
    minutes = xrange(app.config['ONLINE_LASAT_MINUTES'])
    return redis.sunion(['online-users/%d' % (current - x) for x in  minutes])