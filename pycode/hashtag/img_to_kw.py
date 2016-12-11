# coding: utf-8
import logging
import os

from clarifai.client import ApiThrottledError
from clarifai.client import ClarifaiApi
from PIL import Image


# now we are using https://developer.clarifai.com/
# in the future https://aws.amazon.com/ru/rekognition/


class ApiDoesNotWorkException(Exception):
    pass


class ApiIsNotActiveException(Exception):
    pass


class TooLargeImageException(Exception):
    pass


class ClarifAI(object):
    def __init__(self, app_id, app_secret):
        self.api = ClarifaiApi(app_id, app_secret)
        self._init_limits()
        self._check_activity()

    def _init_limits(self):
        info = self.api.get_info()
        self.max_bytes = info[u'max_image_bytes']
        self.max_size = info[u'max_image_size']

    def _get_usage_limits(self):
        usage_data = self.api.get_usage()
        if u'user_throttles' in usage_data:
            month_usage, hour_usage = usage_data[u'user_throttles']
        else:
            logging.exception(u"Unexpected answer from ClarifAI: %s", usage_data)
            raise ApiDoesNotWorkException(u"Unexpected answer from ClarifAI")
        return month_usage, hour_usage

    def _check_activity(self):
        month_usage, hour_usage = self._get_usage_limits()
        if hour_usage[u'consumed'] == hour_usage[u'limit'] or \
                month_usage[u'consumed'] == month_usage[u'limit']:
            raise ApiIsNotActiveException(
                u"The client's limits are exceed: hour=%.2f, month=%.2f" %
                (hour_usage[u'consumed_percentage'], month_usage[u'consumed_percentage'])
            )

    def _get_new_sizes(self, width, height):
        min_dim = min(width, height)
        ratio = min_dim / float(self.max_size)
        return int(width / ratio), int(height / ratio)

    def _prepare_img(self, image_path):
        with Image.open(image_path) as im:
            width, height = im.size

            # resizing
            if min(width, height) > self.max_size:
                width, height = self._get_new_sizes(width, height)
                res_im = im.resize((width, height))
                res_im.save(image_path)
                res_im.close()

        if os.stat(image_path).st_size > self.max_bytes:
            _B_to_kB = lambda x: int(x / 1024.0 / 1024.0)
            raise TooLargeImageException(
                u"The image size (%sKB) is to big, the max is %sKB" %
                (_B_to_kB(os.stat(image_path).st_size), _B_to_kB(self.max_bytes))
            )

    def get_keywords(self, image_path, min_prob=0.9):
        self._prepare_img(image_path)
        with open(image_path) as f:
            try:
                res = self.api.tag((f, "img"))
            except ApiThrottledError:
                self._check_activity()
                logging.error(u"Something went wrong")
                raise ApiDoesNotWorkException(u"Unexpected error")

        res_kws = {}
        if res[u'status_code'] == u'OK' and res[u'results'][0][u'status_code'] == u'OK':
            data = res[u'results'][0]
            kws = data['result']['tag']['classes']
            probs = data['result']['tag']['probs']

            for kw, p in zip(kws, probs):
                if p >= min_prob:
                    res_kws.setdefault(kw.strip(), p)  # it might has duplicate keywords
        return sorted(res_kws.items(), key=lambda x: x[1], reverse=True)


class ImgKeywordDj(object):
    def __init__(self, miner, cache):
        self.miner = miner
        self.cache = cache

    def get_keywords(self, image_path):
        kws = self.cache.get(image_path)
        if kws is None:
            kws = self.miner.get_keywords(image_path)
            self.cache.set(image_path, kws)
        return kws
