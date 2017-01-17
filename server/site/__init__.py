# coding: utf-8

import logging

from flask import Blueprint

site_bp = Blueprint('site_bp', __name__, static_folder='static')
logger = logging.getLogger(__name__)


@site_bp.route('/')
def root():
    return site_bp.send_static_file('index.html')


@site_bp.route('/css/<path:path>')
def send_css(path):
    return site_bp.send_static_file("css/%s" % path)


@site_bp.route('/img/<path:path>')
def send_img(path):
    return site_bp.send_static_file("img/%s" % path)


@site_bp.route('/vendor/<path:path>')
def send_vendor(path):
    return site_bp.send_static_file("vendor/%s" % path)


@site_bp.route('/js/<path:path>')
def send_js(path):
    return site_bp.send_static_file("js/%s" % path)


