# coding: utf-8
from cache import AppCacheRedis
from etc.local.config import CLARIFAI_APP_ID, CLARIFAI_APP_SECRET
from img_to_kw import ClarifAI
from redis import Redis

if __name__ == '__main__':
    cache = AppCacheRedis(Redis())
    im_app = ClarifAI(CLARIFAI_APP_ID, CLARIFAI_APP_SECRET)

    image_path = "/Users/user/Downloads/ialmeida-9d0005ddf4b69c67820a0143f995a3a9-1.jpg"
    kws = cache.get(image_path)
    if kws is None:
        kws = im_app.get_keywords(image_path)
        cache.set(image_path, kws)
        print "NOT"
    else:
        print "HIT"

    print kws
