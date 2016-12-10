# coding: utf-8
import random

import requests

from constants import MAX_TAGS_PER_KW, MIN_TAGS_PER_POST, MAX_TAGS_PER_POST, TRACING_TAG, \
    MOST_POPULAR_HASHTAGS


class HashtagMiner(object):
    def __init__(self, mining_url_template):
        self.mining_url_template = mining_url_template

    def mine(self, keyword):
        resp = requests.get(self.mining_url_template % keyword)
        data = resp.json()

        ht_data = {}
        if data['tagExists']:
            for ht_info in data['results'][:MAX_TAGS_PER_KW]:
                ht_data[ht_info['tag']] = {
                    'relevance': ht_info['relevance'],
                    'rank': ht_info['rank'],  # positively correlates with the number of posts
                }
        return ht_data


class HashtagDj(object):
    def __init__(self, miner, cache):
        self.miner = miner
        self.cache = cache

    @staticmethod
    def _get_kw_key(key):
        return u"kw::%s" % key

    @staticmethod
    def to_instagram(hashtags):
        if isinstance(hashtags, str):
            return u"#%s" % hashtags
        return u" ".join([u"#%s" % tag for tag in hashtags])

    def _mix(self, console):
        result = {}
        if len(console) >= MIN_TAGS_PER_POST:
            sorted_console = sorted(
                console.items(), key=lambda x: (x[1]["relevance"], x[1]["rank"])
            )
            tags = [x[0] for x in sorted_console[-MAX_TAGS_PER_POST:]]
            result["extended"] = False
        else:
            tags = console.keys()
            left_tags_cnt = MIN_TAGS_PER_POST - len(tags)
            tags += random.sample(MOST_POPULAR_HASHTAGS, left_tags_cnt)
            # the data was extended with popular hashtags
            result["extended"] = True

        # adding our tag to trace quality
        tags.append(TRACING_TAG)
        random.shuffle(tags)
        result["tags"] = tags
        return result

    def get_hashtags(self, keywords):
        console = {}
        for kw in keywords:
            key = self._get_kw_key(kw)
            related_tags = self.cache.get(key)

            if related_tags is None:
                related_tags = self.miner.mine(kw)
                self.cache.set(key, related_tags)

            # combining data from different keywords
            for tag, data in related_tags.iteritems():
                if tag in console:
                    if data['relevance'] > console[tag]['relevance']:
                        console[tag] = data
                else:
                    console[tag] = data
        return self._mix(console)

