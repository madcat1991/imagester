# coding: utf-8
import random

import requests
import tweepy
from lxml import html

from constants import MIN_QUOTES_PER_KW


class TwitterQuoteMiner(object):
    def __init__(self, tw_auth):
        auth = tweepy.OAuthHandler(tw_auth["consumer_key"], tw_auth["consumer_secret"])
        auth.set_access_token(tw_auth["access_token"], tw_auth["access_token_secret"])
        self.api = tweepy.API(auth)

    def get_quotes(self, kw):
        q = u'%s #quote filter:safe' % kw
        candidates = []
        for tweet in self.api.search(q=q, rpp=20):
            if tweet.text.find("http") == -1 and \
                    not (hasattr(tweet, "retweeted_status") or hasattr(tweet, "quoted_status")):
                candidates.append((tweet.author.name, tweet.text))
        return candidates if len(candidates) >= MIN_QUOTES_PER_KW else []


class BrainyQuoteMiner(object):
    def get_quotes(self, kw):
        url = "https://www.brainyquote.com/search_results.html"
        resp = requests.get(url, params={"q": kw})

        candidates = []
        if resp.status_code == 200:
            tree = html.fromstring(resp.content)
            is_redirect = len(tree.xpath("//span[@class='h2sub']/a")) > 1

            # right results
            if not is_redirect:
                for div in tree.xpath("//div[@class='boxyPaddingBig']"):
                    quote = div.xpath("./span[@class='bqQuoteLink']/a")[0].text.strip()
                    author = div.xpath("./div[@class='bq-aut']/a")[0].text.strip()
                    candidates.append((author, quote))

        return candidates if len(candidates) >= MIN_QUOTES_PER_KW else []


class QuotesDj(object):
    def __init__(self, miner, cache):
        self.miner = miner
        self.cache = cache

    @staticmethod
    def _get_kw_key(key):
        return u"q::%s" % key

    def get_quotes(self, kws, cnt=3):
        quotes = []
        for kw in kws:
            key = self._get_kw_key(kw)
            quotes = self.cache.get(key)

            if quotes is None:
                quotes = self.miner.get_quotes(kw)
                self.cache.set(key, quotes)

            if len(quotes) >= cnt:
                break
        return quotes[:cnt]
