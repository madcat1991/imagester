# coding: utf-8

import sys

# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'message_only': {
            'format': '%(asctime)s: %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S',
        },
        'basic': {
            'format': '%(asctime)s:%(levelname)s: %(message)s',
        },
        'verbose': {
            'format': '%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s',
        },
        'verbose_with_pid': {
            'format': '%(asctime)s:%(levelname)s:%(name)s.%(funcName)s:%(process)s: %(message)s',
        },
    },
    'handlers': {
        'basic': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': sys.stdout,
        },
        'debug_stdout': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
            'stream': sys.stdout,
        }
    },
    'loggers': {
        'root': {
            'handlers': ['basic'],
        },
        'server': {
            'handlers': ['debug_stdout'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

# connection
PSQL_CONFIG = {
    "host": None,
    "port": None,
    "database": "imagester",
    "user": "imagester",
    "password": None,
    "minconn": 1,
    "maxconn": 10
}

REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

CLARIFAI_KEY = "clarifai"
INIT_CLARIFAI_KEYS = []

REGAIND_KEY = "regaind"
INIT_REGAIND_KEYS = []

# app level configs
MAX_REQUESTS_PER_USER = 10
MAX_IMAGES_PER_REQUEST = 3
DEFAULT_MAX_IMG_BYTES = 10 * 1024 * 1024  # 10MB

IMG_UPLOAD_DIR = "/tmp"

ALLOWED_IMG_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_IMG_SHAPE_FOR_PROCESSING = (1200, 1200)  # pixels

# tags
REL_TAG_URL = None
LOC_TAG_URL = None
MAX_TAGS_TO_MINE = 15
MAX_KWS_TAGS = 20
MAX_LOC_TAGS = 7
KW_TAGS_TTL = 24 * 60 * 60  # 1 day
LOC_TAGS_TTL = 7 * 24 * 60 * 60  # 7 days
LNG_STEP = 0.5
LAT_STEP = 0.5

# quotes
QUOTES_URL = None
QUOTES_TTL = 7 * 24 * 60 * 60  # 7 days
QUOTES_PER_KW = 5
QUOTES_KWS_NUM = 3
MAX_QUOTES = 5

# post time
ENG_DATA_URL = "http://cf.datawrapper.de/Ndpz7/2/data.csv"
ENG_DATA_DIR = "/tmp/eng_data/"

# flask
MAX_CONTENT_LENGTH = MAX_IMAGES_PER_REQUEST * DEFAULT_MAX_IMG_BYTES
