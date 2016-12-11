# coding: utf-8
from flask import Config
from redis import Redis

from cache import AppCacheRedis
from hashtag.img_to_kw import ClarifAI
from hashtag.kw_to_hashtag import HashtagMiner, HashtagDj
from image.ranker import ImgRGBHistRanker

if __name__ == '__main__':
    config = Config('')
    config.from_pyfile("etc/local/config.py")

    img_ranker = ImgRGBHistRanker(config["IMG_DATA_DIR"])
    ranked_images = img_ranker.rank_img_in_dir("data/my_photo")

    cache = AppCacheRedis(Redis())
    im_app = ClarifAI(config["CLARIFAI_APP_ID"], config["CLARIFAI_APP_SECRET"])

    image_path = ranked_images[0][0]
    print image_path

    kws = cache.get(image_path)
    if kws is None:
        kws = im_app.get_keywords(image_path)
        cache.set(image_path, kws)

    miner = HashtagMiner(config["HASHTAG_URL_TEMPLATE"])
    dj = HashtagDj(miner, cache)

    result = dj.get_hashtags(kws)

    print result["extended"]
    print dj.to_instagram(result["tags"])
