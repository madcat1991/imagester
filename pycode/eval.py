# coding: utf-8
from etc.local.config import CLARIFAI_APP_ID, CLARIFAI_APP_SECRET
from img_to_kw import ClarifAI


if __name__ == '__main__':
    image_path = "/Users/user/Downloads/14659329_1616510758655308_3637987881265397760_n.jpg"
    image_path = "/Users/user/Downloads/ialmeida-9d0005ddf4b69c67820a0143f995a3a9-1.jpg"
    im_app = ClarifAI(CLARIFAI_APP_ID, CLARIFAI_APP_SECRET)
    print im_app.get_keywords(image_path)
