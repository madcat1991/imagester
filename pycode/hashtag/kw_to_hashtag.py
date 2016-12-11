# coding: utf-8

import requests

from constants import MAX_TAGS_PER_KW, MAX_TAGS_PER_POST


def f1_score(a, b):
    return 2 * a * b / float(a + b)


class HashtagMiner(object):
    def __init__(self, mining_url_template):
        self.mining_url_template = mining_url_template

    def mine(self, keyword):
        resp = requests.get(self.mining_url_template % keyword)
        data = resp.json()

        ht_data = {}
        if data['tagExists']:
            for ht_info in data['results'][:MAX_TAGS_PER_KW]:
                # simple f1-score
                # rank positively correlates with the number of posts
                ht_data[ht_info['tag']] = f1_score(ht_info['relevance'], ht_info['rank'])
        return ht_data


class HashtagDj(object):
    def __init__(self, miner, cache):
        self.miner = miner
        self.cache = cache

    @staticmethod
    def _get_kw_key(key):
        return u"h::%s" % key

    def get_hashtags(self, keywords):
        console = {}
        for kw in keywords:
            key = self._get_kw_key(kw.replace(" ", ""))
            related_tags = self.cache.get(key)

            if related_tags is None:
                related_tags = self.miner.mine(kw)
                self.cache.set(key, related_tags)

            # combining data from different keywords
            for tag, f1 in related_tags.iteritems():
                if tag not in console or console[tag] < f1:
                    console[tag] = f1
        return sorted(console.items(), key=lambda x: x[1], reverse=True)[:MAX_TAGS_PER_POST]

