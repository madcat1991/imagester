# coding: utf-8
import os
import random

from flask import Config
from redis import Redis

from cache import AppCacheRedis
from constants import TRACING_TAG, MOST_POPULAR_TAGS
from hashtag.img_to_kw import ClarifAI, ImgKeywordDj
from hashtag.kw_to_hashtag import HashtagMiner, HashtagDj
from image.ranker import ImgRGBHistRanker
from quote.explorer import BrainyQuoteMiner, QuotesDj

if __name__ == '__main__':
    config = Config('')
    config.from_pyfile("etc/local/config.py")
    cache = AppCacheRedis(Redis())

    # image
    img_ranker = ImgRGBHistRanker(os.path.join(config["IMG_DATA_DIR"], "hist.npy"))
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
    h_miner = HashtagMiner(config["HASHTAG_URL_TEMPLATE"])
    h_dj = HashtagDj(h_miner, cache)
    tags = h_dj.get_hashtags([k for k, _ in kws])
    print u"Suggested hashtags (based on image):"
    for tag in tags:
        print u"\t%s: %s" % tag

    # TODO hashtags based on location

    print u"Suggested tracing hashtag: ", TRACING_TAG
    print u"5 random popular tags:", random.sample(MOST_POPULAR_TAGS, 5)

    # quotes
    q_miner = BrainyQuoteMiner()
    q_dj = QuotesDj(q_miner, cache)
    best_kws = [kw[0] for kw in kws[:3]]
    quotes = q_dj.get_quotes(best_kws, 5)
    print u"Sample quotes"
    for i, (author, quote) in enumerate(quotes, start=1):
        print u"%s. '%s' - %s" % (i, quote, author)
