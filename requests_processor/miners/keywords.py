# coding: utf-8
from clarifai.client import ApiThrottledError
from clarifai.client import ClarifaiApi

from requests_processor.exceptions import ApiUnexpectedResponseException, ApiIsNotActiveException, \
    ApiUnknownException


class KeywordsMiner(ClarifaiApi):
    def _get_usage_limits(self):
        usage_data = self.get_usage()
        if u'user_throttles' in usage_data:
            month_usage, hour_usage = usage_data[u'user_throttles']
        else:
            raise ApiUnexpectedResponseException(u"Unexpected response: %s", usage_data)
        return month_usage, hour_usage

    def _check_activity(self):
        month_usage, hour_usage = self._get_usage_limits()
        if hour_usage[u'consumed'] == hour_usage[u'limit'] or \
                month_usage[u'consumed'] == month_usage[u'limit']:
            raise ApiIsNotActiveException(
                u"The ClarifAI client's limits are exceed: hour=%.2f, month=%.2f" %
                (hour_usage[u'consumed_percentage'], month_usage[u'consumed_percentage'])
            )

    def get_keywords(self, img_path, min_prob=0.85):
        with open(img_path) as f:
            try:
                res = self.tag((f, "img"))
            except ApiThrottledError as e:
                self._check_activity()
                raise ApiUnknownException(u"Unexpected error: %s", img_path, e)

        res_kws = {}
        if res[u'status_code'] == u'OK' and res[u'results'][0][u'status_code'] == u'OK':
            data = res[u'results'][0]
            kws = data['result']['tag']['classes']
            probs = data['result']['tag']['probs']

            for kw, p in zip(kws, probs):
                _kw = kw.strip()
                if p >= min_prob and (_kw not in res_kws or res_kws[_kw] < p):
                    # it might has duplicate keywords
                    res_kws[_kw] = p

        return sorted(res_kws.items(), key=lambda x: x[1], reverse=True)
