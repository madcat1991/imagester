# coding: utf-8

u"""
The script fills Redis with initial data
"""

import argparse
import json
import logging
import sys

from flask import Config
from redis import Redis

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', required=True, dest="config_path",
                        help=u'Path to the configuration file')
    parser.add_argument("--log-level", default='INFO', dest="log_level",
                        choices=['DEBUG', 'INFO', 'WARNINGS', 'ERROR'], help=u"Logging level")
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s', stream=sys.stdout, level=getattr(logging, args.log_level)
    )

    # load config
    config = Config('')
    config.from_pyfile(args.config_path)

    # redis
    r = Redis(**config['REDIS_CONFIG'])

    logging.info(u"Warming up redis")

    # clarifai
    clarifai_keys = [json.dumps(pair) for pair in config["INIT_CLARIFAI_KEYS"]]
    with r.pipeline() as pipe:
        key = config["CLARIFAI_KEY"]
        pipe.delete(key)
        pipe.rpush(key, *clarifai_keys)
        pipe.execute()
    logging.info(u"%s clarifai keys have been inserted", len(clarifai_keys))

    # regaind
    regaind_keys = [json.dumps(pair) for pair in config["INIT_REGAIND_KEYS"]]
    with r.pipeline() as pipe:
        key = config["REGAIND_KEY"]
        pipe.delete(key)
        pipe.rpush(key, *regaind_keys)
        pipe.execute()
    logging.info(u"%s regaind keys have been inserted", len(regaind_keys))

    logging.info(u"Finished")
