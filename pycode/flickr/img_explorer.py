# coding: utf-8

import argparse
import glob
import logging
import os
import urllib
from datetime import date, timedelta

import requests
import shutil

import sys
from flask import Config


INTERESTING_URL_TEMPLATE = "https://farm%(farm)s.staticflickr.com/%(server)s/%(id)s_%(secret)s_%(size)s.jpg"


def to_url(p_data, size="b"):
    p_data["size"] = size
    return INTERESTING_URL_TEMPLATE % p_data


def collect_image_urls(config):
    api_url = "https://api.flickr.com/services/rest/"
    req_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    params = {
        "method": "flickr.interestingness.getList",
        "format": "json",
        "api_key": config["FLICKR_API_KEY"],
        "nojsoncallback": 1,
        "per_page": 500,
        "date": req_date
    }

    resp = requests.get(api_url, params=params)
    data = resp.json()

    urls = [to_url(p_data) for p_data in data["photos"]["photo"]]
    return urls


def update_photos(urls, config):
    img_dir = config["FLICKR_IMG_DIR"]
    tmp_dir = os.path.join(img_dir, "tmp")

    if os.path.exists(tmp_dir):
        logging.info(u"Removing existing tmp folder %s", tmp_dir)
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)

    logging.info(u"Starting to download files to %s", tmp_dir)
    for i, url in enumerate(urls):
        if i % 100 == 0:
            logging.info(u"Download %s/%s", i, len(urls))

        path_to_save = os.path.join(tmp_dir, "%s.jpg" % i)
        urllib.urlretrieve(url, path_to_save)
    logging.info(u"Images have been downloaded")

    logging.info(u"Removing old files from %s", img_dir)
    for path in glob.glob(os.path.join(img_dir, "*.jpg")):
        os.unlink(path)
    logging.info(u"Old files have been removed")

    logging.info(u"Copying new files to %s", img_dir)
    for path in glob.glob(os.path.join(tmp_dir, "*.jpg")):
        shutil.copy(path, img_dir)
    logging.info(u"New files have been copied")

    logging.info(u"Removing existing tmp folder %s", tmp_dir)
    os.makedirs(tmp_dir)


def main():
    if os.path.exists(args.config_path):
        config = Config('')
        config.from_pyfile(args.config_path)
    else:
        raise Exception(u"Config file '%s' doesn't exist", args.config_path)

    new_urls = collect_image_urls(config)
    update_photos(new_urls, config)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', required=True, dest="config_path",
                        help=u'Configuration file absolute path')
    parser.add_argument("--log-level", default='INFO', dest="log_level",
                        choices=['DEBUG', 'INFO', 'WARNINGS', 'ERROR'], help=u"Logging level")
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s', stream=sys.stdout, level=getattr(logging, args.log_level)
    )

    main()
