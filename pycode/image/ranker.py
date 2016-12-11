# coding: utf-8

import glob
import os

import cv2
import numpy as np

from image.common import get_img_hist


class ImgRGBHistRanker(object):
    def __init__(self, matrix_path):
        self.brg_matrix = np.load(matrix_path)

    def rank_img_in_dir(self, dir_path):
        res = []
        for path in glob.glob(os.path.join(dir_path, "*.jpg")):
            im_hist = get_img_hist(path)
            scores = [cv2.compareHist(im_hist, row, cv2.HISTCMP_CHISQR) for row in self.brg_matrix]
            res.append((path, np.mean(scores)))
        return sorted(res, key=lambda x: x[1])
