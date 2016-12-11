# coding: utf-8
from flask import Config

from cache import AppCacheRedis
from image.ranker import ImgRGBHistRanker
from img_to_kw import ClarifAI
from redis import Redis

from kw_to_hashtag import HashtagMiner, HashtagDj

if __name__ == '__main__':
    config = Config('')
    config.from_pyfile("etc/local/config.py")

    img_ranker = ImgRGBHistRanker(config["IMG_DATA_DIR"])
    ranked_images = img_ranker.rank_img_in_dir("data/my_photo")

    cache = AppCacheRedis(Redis())
    im_app = ClarifAI(config["CLARIFAI_APP_ID"], config["CLARIFAI_APP_SECRET"])

    image_path = ranked_images[0][0]
    kws = cache.get(image_path)
    if kws is None:
        kws = im_app.get_keywords(image_path)
        cache.set(image_path, kws)

    miner = HashtagMiner(config["HASHTAG_URL_TEMPLATE"])
    dj = HashtagDj(miner, cache)

    result = dj.get_hashtags(kws)

    print image_path
    print result["extended"]
    print dj.to_instagram(result["tags"])
