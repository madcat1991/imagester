# coding: utf-8

import json
import logging
import logging.config

import psycopg2
import psycopg2.extensions
from clarifai.client import ClarifaiApi
from flask import Flask, jsonify
from psycopg2.pool import ThreadedConnectionPool
from redis import Redis

from server.exceptions import BaseApiException
from server.functions import get_abs_path


logger = logging.getLogger(__name__)


def handle_exception_with_as_dict_method(error):
    logger.error(error)
    return jsonify(error.as_dict())


class ApiAppJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class APIApp(Flask):
    def __init__(self, *args, **kwargs):
        super(APIApp, self).__init__(*args, **kwargs)
        self.response_class.default_mimetype = 'application/json'

    def _load_config(self, config_path):
        if not config_path.startswith('/'):
            config_path = get_abs_path('etc', config_path, 'config.py')
        self.config.from_pyfile(config_path)

    def _setup_logger(self):
        logging_options = self.config.get('LOGGING', {})
        self.logger.handlers = []
        logging.config.dictConfig(logging_options)
        logger.info(u"Logger has been setuped")

    def _init_redis(self):
        conf = self.config['REDIS_CONFIG']
        self.redis = Redis(**conf)
        logger.info(
            u"Redis has been initialized: host=%s, port=%s, db=%s",
            conf["host"], conf["port"], conf["db"]
        )

    def _init_psql(self):
        conf = self.config['PSQL_CONFIG']
        psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
        self.pool = ThreadedConnectionPool(**conf)
        logger.info(
            u"DB has been initialized: host=%s, port=%s, db=%s, user=%s, min_conn=%s, max_conn=%s",
            conf["host"], conf["port"], conf["database"], conf["user"], conf["minconn"], conf["maxconn"]
        )

    def _init_clarifai_limits(self):
        app_id, app_secret = json.loads(self.redis.lrange("clarifai", 0, 0)[0])
        api = ClarifaiApi(app_id, app_secret)
        info = api.get_info()
        self.max_image_bytes = info.get(u'max_image_bytes', self.config['DEFAULT_MAX_IMG_BYTES'])

    def init(self, config_path):
        self._load_config(config_path)
        self._setup_logger()
        self._init_psql()
        self._init_redis()
        self._init_clarifai_limits()
        logger.info(u"API has been initialized")

    def setup_error_handlers(self):
        self.register_error_handler(BaseApiException, handle_exception_with_as_dict_method)

    def make_response(self, rv):
        if isinstance(rv, self.response_class):
            return rv
        if isinstance(rv, (dict, list)):
            rv = json.dumps(rv, cls=ApiAppJsonEncoder)
        elif isinstance(rv, bool):
            rv = "true" if rv else "false"
        return super(APIApp, self).make_response(rv)
