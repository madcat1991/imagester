# coding: utf-8
import json
import requests

from requests_processor.functions import f1_score, lat_lng_to_grid


class TagsMiner(object):
    def __init__(self, r, url, max_tags_to_mine, ttl_sec):
        """Getting tags for keywords

        :param r: redis
        :param url: url to mine tags
        :param max_tags_to_mine: maximum number of mining tags
        :param ttl_sec: ttl for mined tags in cache
        """
        self.r = r
        self.url = url
        self.max_tags_to_mine = max_tags_to_mine
        self.ttl_sec = ttl_sec

        self.key_template = u"kw::%s"

    def _mine(self, base_tag):
        resp = requests.get(self.url + base_tag)
        data = resp.json()

        ht_data = {}
        if data['tagExists']:
            for ht_info in data['results'][:self.max_tags_to_mine]:
                # rank positively correlates with the number of posts
                ht_data[ht_info['tag']] = f1_score(ht_info['relevance'], ht_info['rank'])
        return ht_data

    def _get_tags_by_kw(self, kw):
        base_tag = kw.replace(" ", "")
        key = self.key_template % base_tag
        tags = self.r.get(key)
        if tags is None:
            tags = self._mine(base_tag)
            self.r.set(key, json.dumps(tags), self.ttl_sec)
        else:
            tags = json.loads(tags)
        return tags

    def get_tags(self, keywords, top):
        console = {}
        for kw in keywords:
            tags = self._get_tags_by_kw(kw)

            # combining data from different keywords
            for tag, f1 in tags.iteritems():
                if tag not in console or console[tag] < f1:
                    console[tag] = f1

        sorted_tags = sorted(console.items(), key=lambda x: x[1], reverse=True)[:top]
        return [tag for tag, _ in sorted_tags]


class LocTagsMiner(object):
    def __init__(self, r, url, ttl_sec, lat_step, lng_step):
        self.r = r
        self.url = url
        self.ttl_sec = ttl_sec

        self.key_template = u"loc::%s"

        self.lat_step = lat_step
        self.lng_step = lng_step

    def _mine(self, lat, lng):
        bbox = map(
            str,
            (lng - self.lng_step, lat - self.lat_step, lng + self.lng_step, lat + self.lat_step)
        )
        params = {
            "bbox": ",".join(bbox),
            "zoom": 12
        }

        ht_data = {}
        resp = requests.get(self.url, params)
        if resp.status_code == 200:
            data = resp.json()
            ht_data = {ht_info["tag"]: ht_info["weight"] for ht_info in data['tags']}
        return ht_data

    def _get_tags_by_loc(self, lat, lng):
        grid_sqr = lat_lng_to_grid(lat, lng)
        key = self.key_template % grid_sqr
        tags = self.r.get(key)
        if tags is None:
            tags = self._mine(lat, lng)
            self.r.set(key, json.dumps(tags), self.ttl_sec)
        else:
            tags = json.loads(tags)
        return tags

    def get_tags(self, lat, lng, top):
        tags = self._get_tags_by_loc(lat, lng)
        sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:top]
        return [tag for tag, _ in sorted_tags]
