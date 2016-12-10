# coding: utf-8

import json
from constants import CACHE_TTL_SEC


class AppCacheRedis(object):
    def __init__(self, redis_inst):
        self.r = redis_inst

    def get(self, key):
        obj = self.r.get(key)
        return json.loads(obj) if obj is not None else obj

    def set(self, key, obj):
        value = json.dumps(obj)
        self.r.set(key, value, CACHE_TTL_SEC)
