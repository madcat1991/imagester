# coding: utf-8
import cv2


def get_img_hist(img_path):
    img = cv2.imread(img_path)
    # colors scheme is BRG
    hist = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist.flatten()
