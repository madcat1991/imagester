# coding: utf-8

u"""
This script creates red, green and blue histogram matrices for
last day interesting images from flickr
"""

import argparse
import glob
import logging
import os
import urllib
import cv2
from datetime import date, timedelta
from multiprocessing.dummy import Pool

import numpy as np
import requests
import shutil

import sys
from flask import Config
from sklearn.preprocessing import normalize

IMG_URL_TEMPLATE = "https://farm%(farm)s.staticflickr.com/%(server)s/%(id)s_%(secret)s_%(size)s.jpg"


def get_img_url(p_data, size="b"):
    p_data["size"] = size
    return IMG_URL_TEMPLATE % p_data


def collect_image_urls(config):
    logging.info(u"Collecting image urls")
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

    urls = [get_img_url(p_data) for p_data in data["photos"]["photo"]]
    logging.info(u"%s urls have been collected", len(urls))
    return urls


def download_images(urls, dir_path, n_threads):
    logging.info(u"Download images to %s", dir_path)

    if os.path.exists(dir_path):
        logging.info(u"Removing existing folder %s", dir_path)
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)

    logging.info(u"Starting to download files")

    def _thread_func(pos):
        path_to_save = os.path.join(dir_path, "%s.jpg" % pos)
        urllib.urlretrieve(urls[pos], path_to_save)

    pool = Pool(n_threads)
    pool.map(_thread_func, range(len(urls)))

    logging.info(u"Images have been downloaded")


def prepare_rgb_matrices(dir_path):
    logging.info(u"Building rgb matrices")
    colors = ("r", "g", "b")
    matrices = {col: [] for col in colors}

    logging.info(u"Collecting histograms")
    for path in glob.glob(os.path.join(dir_path, "*.jpg")):
        img = cv2.imread(path)
        for i, col in enumerate(colors):
            hist = cv2.calcHist([img], [i], None, [256], [0, 256])
            matrices[col].append(hist.reshape(-1))

    logging.info(u"Creating matrices and saving")
    for color, data in matrices.iteritems():
        m = normalize(np.array(data))
        path = os.path.join(dir_path, "%s.npy" % color)
        np.save(path, m)
        logging.info(u"Saved matrix %s to %s", color, path)
    logging.info(u"RGB matrices have been created")


def replace_files(src_dir, dest_dir):
    logging.info(u"Removing old files from %s", dest_dir)
    for path in glob.glob(os.path.join(dest_dir, "*.*")):
        os.unlink(path)
    logging.info(u"Old files have been removed")

    logging.info(u"Copying new files to %s", dest_dir)
    for path in glob.glob(os.path.join(src_dir, "*.*")):
        shutil.copy(path, dest_dir)
    logging.info(u"New files have been copied")

    logging.info(u"Removing folder %s", src_dir)
    shutil.rmtree(src_dir)


def main():
    if os.path.exists(args.config_path):
        config = Config('')
        config.from_pyfile(args.config_path)
    else:
        raise Exception(u"Config file '%s' doesn't exist", args.config_path)

    new_urls = collect_image_urls(config)

    img_dir = config["FLICKR_IMG_DIR"]
    tmp_dir = os.path.join(img_dir, "tmp")

    download_images(new_urls, tmp_dir, args.n_threads)
    prepare_rgb_matrices(tmp_dir)
    replace_files(tmp_dir, img_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', required=True, dest="config_path",
                        help=u'Configuration file absolute path')
    parser.add_argument('-j', default=4, dest="n_threads",
                        help=u'Number of images downloading threads. Default: 4')
    parser.add_argument("--log-level", default='INFO', dest="log_level",
                        choices=['DEBUG', 'INFO', 'WARNINGS', 'ERROR'], help=u"Logging level")
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s', stream=sys.stdout, level=getattr(logging, args.log_level)
    )

    main()
