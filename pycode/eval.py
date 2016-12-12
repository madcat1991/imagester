# coding: utf-8
import os
import random

from flask import Config
from redis import Redis

from cache import AppCacheRedis
from constants import TRACING_TAG, MOST_POPULAR_TAGS, WEEKDAYS
from hashtag.img_to_kw import ClarifAI, ImgKeywordDj
from hashtag.kw_to_hashtag import HashtagMiner, HashtagDj
from image.loc_from_img import get_lat_lon
from image.ranker import ImgRGBHistRanker
from quote.explorer import BrainyQuoteMiner, QuotesDj
from eng_time.engagement import EngTimeMiner

if __name__ == '__main__':
    config = Config('')
    config.from_pyfile("etc/local/config.py")
    cache = AppCacheRedis(Redis())

    # image
    img_ranker = ImgRGBHistRanker(os.path.join(config["DATA_DIR"], "hist.npy"))
    ranked_images = img_ranker.rank_img_in_dir("data/my_photo")
    image_path = ranked_images[0][0]
    print u"Suggested image to publish:", image_path

    # keywords
    kw_miner = ClarifAI(config["CLARIFAI_APP_ID"], config["CLARIFAI_APP_SECRET"])
    kw_dj = ImgKeywordDj(kw_miner, cache)
    kws = kw_dj.get_keywords(image_path)
    print u"Image keywords:"
    for kw in kws:
        print u"\t%s: %s" % kw

    # hashtags
    h_miner = HashtagMiner(config)
    h_dj = HashtagDj(h_miner, cache)
    tags = h_dj.get_hashtags_by_kws([k for k, _ in kws])
    print u"Suggested hashtags (based on image):"
    for tag in tags:
        print u"\t%s: %s" % tag

    lat, lng = get_lat_lon(image_path)
    if lat and lng:
        loc_tags = h_dj.get_hashtags_by_loc(lat, lng)
        print u"Suggested hashtags (based on location):"
        for tag in loc_tags:
            print u"\t%s: %s" % tag

    print u"Tracing hashtag:", TRACING_TAG
    print u"5 random popular tags:", random.sample(MOST_POPULAR_TAGS, 5)

    # quotes
    q_miner = BrainyQuoteMiner()
    q_dj = QuotesDj(q_miner, cache)
    best_kws = [kw[0] for kw in kws[:3]]
    quotes = q_dj.get_quotes(best_kws, 5)
    print u"Sample quotes"
    for i, (author, quote) in enumerate(quotes, start=1):
        print u"%s. '%s' - %s" % (i, quote, author)

    # time
    t_miner = EngTimeMiner(config["ENG_DATA_URL"], config["DATA_DIR"])
    closest24, best24 = t_miner.get_eng_time()
    print u"Suggested closest time to post (in next 24h): %s, %s:00" % \
          (WEEKDAYS[closest24[0]], str(closest24[1]).zfill(2))
    print u"Suggested best time to post (in next 24h): %s, %s:00" % \
          (WEEKDAYS[best24[0]], str(best24[1]).zfill(2))
