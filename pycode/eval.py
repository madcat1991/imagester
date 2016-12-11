# coding: utf-8
from flask import Config
from redis import Redis

from cache import AppCacheRedis
from hashtag.img_to_kw import ClarifAI, ImgKeywordDj
from hashtag.kw_to_hashtag import HashtagMiner, HashtagDj
from image.ranker import ImgRGBHistRanker
from quote.explorer import BrainyQuoteMiner, QuotesDj

if __name__ == '__main__':
    config = Config('')
    config.from_pyfile("etc/local/config.py")
    cache = AppCacheRedis(Redis())

    # image
    img_ranker = ImgRGBHistRanker(config["IMG_DATA_DIR"])
    ranked_images = img_ranker.rank_img_in_dir("data/my_photo")
    print ranked_images
    image_path = ranked_images[0][0]
    print image_path

    # keywords
    kw_miner = ClarifAI(config["CLARIFAI_APP_ID"], config["CLARIFAI_APP_SECRET"])
    kw_dj = ImgKeywordDj(kw_miner, cache)
    kws = kw_dj.get_keywords(image_path)
    print kws

    # hashtags
    h_miner = HashtagMiner(config["HASHTAG_URL_TEMPLATE"])
    h_dj = HashtagDj(h_miner, cache)
    tags_res = h_dj.get_hashtags([k for k, _ in kws])
    print tags_res["extended"]
    print h_dj.to_instagram(tags_res["tags"])

    # quotes
    best_kws = [kw[0] for kw in kws[:3]]
    print u"Best top3 kw:", best_kws
    q_miner = BrainyQuoteMiner()
    q_dj = QuotesDj(q_miner, cache)
    quotes = q_dj.get_quotes(best_kws, 5)
    print quotes
