# coding: utf-8


CACHE_TTL_SEC = 24 * 60 * 60
MAX_TAGS_PER_KW = 20

# originally Instagram allows 30, but this number also includes
# users mentioned in the post
MAX_TAGS_PER_POST = 20
MIN_TAGS_PER_POST = 10

MOST_POPULAR_TAGS = [
    u'TFLers', u'TagsForLikes', u'all_shots', u'amazing', u'awesome', u'bestoftheday',
    u'cool', u'followme', u'funny', u'hot', u'igaddict', u'igers', u'instacool',
    u'instadaily', u'instafollow', u'instago', u'instagood', u'instagramers',
    u'instahub', u'instalike', u'life', u'like4like', u'photo', u'photooftheday',
    u'picoftheday', u'statigram', u'webstagram',
]
TRACING_TAG = u'imagester'
