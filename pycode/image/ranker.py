# coding: utf-8

import glob
import os

import cv2
import numpy as np
from sklearn.preprocessing import normalize


class ImgRGBHistRanker(object):
    def __init__(self, matrices_dir):
        self._colors = ("r", "g", "b")
        self._load_matrices(matrices_dir)

    def _load_matrices(self, dir_path):
        self.hist_ms = {}
        for color in self._colors:
            m_path = os.path.join(dir_path, "%s.npy" % color)
            self.hist_ms[color] = np.load(m_path)

    def rank_img_in_dir(self, dir_path):
        res = []

        for path in glob.glob(os.path.join(dir_path, "*.jpg")):
            scores = []
            img = cv2.imread(path)

            for i, color in enumerate(self._colors):
                hist = cv2.calcHist([img], [i], None, [256], [0, 256])
                img_hist_col = normalize(hist, axis=0)

                scores.append(np.mean(np.dot(self.hist_ms[color], img_hist_col)))

            res.append((path, np.mean(scores)))
        return sorted(res, key=lambda x: x[1], reverse=True)
