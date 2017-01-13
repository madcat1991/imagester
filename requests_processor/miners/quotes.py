# coding: utf-8
import json
import random

import requests
from lxml import html


class QuotesMiner(object):
    def __init__(self, r, url, max_quotes_to_mine, ttl_sec):
        self.r = r
        self.url = url
        self.max_quotes_to_mine = max_quotes_to_mine
        self.ttl_sec = ttl_sec

        self.key_template = u"qt:%s"

    def _mine(self, kw):
        resp = requests.get(self.url, params={"q": kw})

        candidates = []
        if resp.status_code == 200:
            tree = html.fromstring(resp.content)
            is_redirect = len(tree.xpath("//span[@class='h2sub']/a")) > 1

            # right results
            if not is_redirect:
                for div in tree.xpath("//div[@class='boxyPaddingBig']")[:self.max_quotes_to_mine]:
                    quote = div.xpath("./span[@class='bqQuoteLink']/a")[0].text.strip()
                    author = div.xpath("./div[@class='bq-aut']/a")[0].text.strip()
                    candidates.append(u"%s (%s)" % (quote, author))
        return candidates

    def _get_quotes_by_kw(self, kw):
        key = self.key_template % kw.replace(" ", "")
        quotes = self.r.get(key)
        if quotes is None:
            quotes = self._mine(kw)
            self.r.set(key, json.dumps(quotes), self.ttl_sec)
        else:
            quotes = json.loads(quotes)
        return quotes

    def get_quotes(self, keywords, top):
        quotes = set()
        for kw in keywords:
            quotes.update(self._get_quotes_by_kw(kw))

        if len(quotes) > top:
            quotes = random.sample(quotes, top)
        return list(quotes)
