# coding: utf-8
from cache import AppCacheRedis
from etc.local.config import CLARIFAI_APP_ID, CLARIFAI_APP_SECRET, HASHTAG_URL_TEMPLATE
from img_to_kw import ClarifAI
from redis import Redis

from kw_to_hashtag import HashtagMiner, HashtagDj

if __name__ == '__main__':
    cache = AppCacheRedis(Redis())
    im_app = ClarifAI(CLARIFAI_APP_ID, CLARIFAI_APP_SECRET)

    image_path = "/Users/user/Downloads/ialmeida-9d0005ddf4b69c67820a0143f995a3a9-1.jpg"
    kws = cache.get(image_path)
    if kws is None:
        kws = im_app.get_keywords(image_path)
        cache.set(image_path, kws)

    miner = HashtagMiner(HASHTAG_URL_TEMPLATE)
    dj = HashtagDj(miner, cache)

    result = dj.get_hashtags(kws)
    print result["extended"]
    print dj.to_instagram(result["tags"])
