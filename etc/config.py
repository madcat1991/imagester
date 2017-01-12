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
        'api': {
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
    "maxconn": 20
}

REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

INIT_CLARIFAI_KEYS = []

# app level configs
MAX_REQUESTS_PER_USER = 5
MAX_IMAGES_PER_REQUEST = 3
ALLOWED_IMG_EXTENSIONS = {'png', 'jpg', 'jpeg'}
IMG_UPLOAD_DIR = "/tmp"
