# coding: utf-8

u"""
The script processes user requests
"""

import argparse
import glob
import json
import logging
import os
import sys
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

import psycopg2
from flask import Config
from redis import Redis

from requests_processor.exceptions import ApiUnknownException, ApiUnexpectedResponseException, \
    ApiIsNotActiveException
from requests_processor.image import shape_image, get_lat_lon
from requests_processor.miners.keywords import KeywordsMiner
from requests_processor.miners.post_time import PostTimeMiner
from requests_processor.miners.quotes import QuotesMiner
from requests_processor.miners.best_image import BestImageMiner
from requests_processor.miners.tags import TagsMiner, LocTagsMiner


def get_best_image(img_dir_path):
    best_img = None
    best_metric = -1

    for img_path in glob.glob(os.path.join(img_dir_path, "*.*")):
        shape_image(img_path, config["MAX_IMG_SHAPE_FOR_PROCESSING"])

        metric = 0
        keys_and_secrets = r.lrange(config["REGAIND_KEY"], 0, -1)
        for key_and_secret in keys_and_secrets:
            key, secret = json.loads(key_and_secret)
            client = BestImageMiner(key, secret)

            try:
                metric = client.get_imagester_metric(img_path)
            except ApiUnknownException as e:
                logging.exception(u"Image %s: %s", img_path, e)
                return None
            except ApiUnexpectedResponseException as e:
                logging.exception(u"Image %s: %s", img_path, e)
                continue
            else:
                break

        if metric > best_metric:
            best_img = img_path
            best_metric = metric
    return best_img


def get_keywords(img_path):
    keys_and_secrets = r.lrange(config["CLARIFAI_KEY"], 0, -1)
    for key_and_secret in keys_and_secrets:
        key, secret = json.loads(key_and_secret)

        client = KeywordsMiner(key, secret)
        try:
            keywords = client.get_keywords(img_path)
        except ApiUnknownException as e:
            logging.exception(u"Image %s: %s", img_path, e)
            return None
        except ApiUnexpectedResponseException as e:
            logging.exception(u"Image %s: %s", img_path, e)
            return None
        except ApiIsNotActiveException:
            continue
        else:
            return keywords
    return None


def process(params):
    req_id, utc_offset_minutes, img_dir = params
    img_dir_path = os.path.join(config['IMG_UPLOAD_DIR'], img_dir)

    # suggesting image
    best_img_path = get_best_image(img_dir_path)
    if best_img_path is not None:
        # identifying the image's keywords
        keywords = get_keywords(best_img_path)
        if keywords is not None and keywords:
            keywords = [kw for kw, _ in keywords]
            # tags by keywords
            tags = kw_tagger.get_tags(keywords, config["MAX_KWS_TAGS"])
            if tags:
                loc_tags = []

                # identifying the image's location if it is possible
                _, best_img_ext = os.path.splitext(best_img_path)
                if best_img_ext.lower() in ('.jpg', '.jpeg'):
                    lat, lng = get_lat_lon(best_img_path)
                    # tags by loc
                    if lat and lng:
                        loc_tags = loc_tagger.get_tags(lat, lng, config["MAX_LOC_TAGS"])

                # quotes
                quotes = quotter.get_quotes(keywords[:config["QUOTES_KWS_NUM"]], config["MAX_QUOTES"])

                # publishing time
                user_pt_closest, user_pt_in_24h = time_miner.get_best_times(utc_offset_minutes)

                rel_img_path = os.path.relpath(best_img_path, config['IMG_UPLOAD_DIR'])
                return req_id, rel_img_path, tags, loc_tags, quotes, user_pt_closest, user_pt_in_24h
    return None


def main():
    with conn.cursor() as cur:
        sql = """
            SELECT id, utc_offset_minutes, img_dir FROM request
            WHERE id NOT IN (SELECT request_id FROM processed_request)
            ORDER BY dt LIMIT %s
        """
        cur.execute(sql, (args.batch_size,))
        suggestion_reqs = cur.fetchall()
    logging.info(u"Number of requests to process: %s", len(suggestion_reqs))

    pool = ThreadPool()
    processed = []
    for res in pool.map(process, suggestion_reqs):
        if res is not None:
            processed.append(res)
    logging.info(u"Number of processed requests: %s", len(processed))

    logging.info(u"Inserting to DB")
    with conn.cursor() as cur:
        for res in processed:
            req_id, img_path, tags, loc_tags, quotes, pt_closest, pt_in_24h = res
            sql = """
                INSERT INTO processed_request (
                    request_id,
                    img_path,
                    tags,
                    loc_tags,
                    quotes,
                    user_pt_closest,
                    user_pt_in_24h
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (req_id, img_path, tags, loc_tags, quotes, pt_closest, pt_in_24h))
        conn.commit()
    logging.info(u"Finish")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', required=True, dest="config_path",
                        help=u'Path to the configuration file')
    parser.add_argument('-j', default=cpu_count(), dest="worker_num",
                        help=u'Number of parallel workers. By default: %s' % cpu_count())
    parser.add_argument('-b', default=1000, dest="batch_size",
                        help=u'Number of requests to process. By default: 1000')
    parser.add_argument("--log-level", default='INFO', dest="log_level",
                        choices=['DEBUG', 'INFO', 'WARNINGS', 'ERROR'], help=u"Logging level")
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s', stream=sys.stdout, level=getattr(logging, args.log_level)
    )

    # load config
    config = Config('')
    config.from_pyfile(args.config_path)

    # psql
    db_conf = config['PSQL_CONFIG']
    conn = psycopg2.connect(
        host=db_conf['host'], port=db_conf['port'],
        database=db_conf['database'], user=db_conf['user'],
        password=db_conf['password']
    )

    # redis
    r = Redis(**config['REDIS_CONFIG'])
    # static miners
    kw_tagger = TagsMiner(
        r, config["REL_TAG_URL"], config["MAX_TAGS_TO_MINE"], config["KW_TAGS_TTL"]
    )
    loc_tagger = LocTagsMiner(
        r, config["LOC_TAG_URL"], config["KW_TAGS_TTL"], config["LAT_STEP"], config["LNG_STEP"],
    )
    quotter = QuotesMiner(
        r, config["QUOTES_URL"], config["QUOTES_PER_KW"], config["QUOTES_TTL"]
    )
    time_miner = PostTimeMiner(config["ENG_DATA_URL"], config["ENG_DATA_DIR"])

    main()
