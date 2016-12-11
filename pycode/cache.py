# coding: utf-8
import cPickle

from constants import CACHE_TTL_SEC


class AppCacheRedis(object):
    def __init__(self, redis_inst):
        self.r = redis_inst

    def get(self, key):
        obj = self.r.get(key)
        return cPickle.loads(obj) if obj is not None else obj

    def set(self, key, obj):
        value = cPickle.dumps(obj, 2)
        self.r.set(key, value, CACHE_TTL_SEC)
