# coding: utf-8

import requests

from constants import MAX_TAGS_PER_KW, MAX_REL_TAGS_PER_POST, LNG_STEP, LAT_STEP, MAX_LOC_TAGS_PER_POST


def f1_score(a, b):
    return 2 * a * b / float(a + b)


class HashtagMiner(object):
    def __init__(self, config):
        self.rel_tag_url_template = config['REL_TAG_URL_TEMPLATE']
        self.loc_tag_url = config['LOC_TAG_URL']

    def mine_kw(self, keyword):
        resp = requests.get(self.rel_tag_url_template % keyword)
        data = resp.json()

        ht_data = {}
        if data['tagExists']:
            for ht_info in data['results'][:MAX_TAGS_PER_KW]:
                # simple f1-score
                # rank positively correlates with the number of posts
                ht_data[ht_info['tag']] = f1_score(ht_info['relevance'], ht_info['rank'])
        return ht_data

    def mine_loc(self, lat, lng):
        bbox = map(str, (lng - LNG_STEP, lat - LAT_STEP, lng + LNG_STEP, lat + LAT_STEP))
        params = {
            "bbox": ",".join(bbox),
            "zoom": 12
        }

        ht_data = {}
        resp = requests.get(self.loc_tag_url, params)
        if resp.status_code == 200:
            data = resp.json()
            ht_data = {ht_info["tag"]: ht_info["weight"] for ht_info in data['tags']}
        return ht_data


class HashtagDj(object):
    def __init__(self, miner, cache):
        self.miner = miner
        self.cache = cache

    @staticmethod
    def _get_kw_key(key):
        return u"h::%s" % key

    def get_hashtags_by_kws(self, keywords):
        console = {}
        for kw in keywords:
            key = self._get_kw_key(kw.replace(" ", ""))
            related_tags = self.cache.get(key)

            if related_tags is None:
                related_tags = self.miner.mine_kw(kw)
                self.cache.set(key, related_tags)

            # combining data from different keywords
            for tag, f1 in related_tags.iteritems():
                if tag not in console or console[tag] < f1:
                    console[tag] = f1
        return sorted(console.items(), key=lambda x: x[1], reverse=True)[:MAX_REL_TAGS_PER_POST]

    def lat_lng_to_grid(self, lat, lng):
        lng_letter_A = chr(64 + int((lng + 180) / 20) + 1)
        remainder = (lng + 180) % 20
        lng_num = int(remainder / 2)
        remainder %= 2
        lng_letter_a = chr(96 + int(remainder * 12 + 1))

        lat_letter_A = chr(64 + int((lat + 90) / 10) + 1)
        remainder = (lat + 90) % 10
        lat_num = int(remainder)
        remainder -= lat_num
        lat_letter_a = chr(96 + int(remainder * 24 + 1))
        return u"%s%s%s%s%s%s" % (lng_letter_A, lat_letter_A, lng_num, lat_num, lng_letter_a, lat_letter_a)

    def get_hashtags_by_loc(self, lat, lng):
        grid_sqr = self.lat_lng_to_grid(lat, lng)
        key = self._get_kw_key(grid_sqr)
        loc_tags = self.cache.get(key)

        if loc_tags is None:
            loc_tags = self.miner.mine_loc(lat, lng)
            loc_tags = sorted(loc_tags.items(), key=lambda x: x[1], reverse=True)[:MAX_LOC_TAGS_PER_POST]
            self.cache.set(key, loc_tags)

        return loc_tags
