# coding: utf-8

import logging

from flask import Blueprint
from flask import current_app
from flask import request


from server.exceptions import ArgErrorException
from server.functions import check_email, check_images, prepare_request

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@api_bp.route('/')
def root():
    return api_bp.send_static_file('index.html')


@api_bp.route('/ping/')
def ping_handler():
    """Ping-pong command
    """
    return {"result": "pong"}


@api_bp.route('/check_email/')
def check_email_handler():
    email = request.args.get("email")
    return check_email(email)


@api_bp.route('/upload/', methods=["POST"])
def upload_handler():
    email = request.form.get("email")
    email_check_res = check_email(email)

    utc_offset_minutes = request.form.get("offset_minutes", type=int, default=0)

    if email_check_res["is_ok"]:
        images = [img for img in request.files.getlist("images") if img.filename]
        images = images[: current_app.config["MAX_IMAGES_PER_REQUEST"]]
        images_check_res = check_images(images)

        if images_check_res["is_ok"]:
            attempts_left = prepare_request(email, utc_offset_minutes, images)
        else:
            raise ArgErrorException(
                "images", images_check_res["msg"], filename=images_check_res.get("filename", "")
            )
    else:
        raise ArgErrorException("email", email_check_res["msg"], limit=email_check_res.get("limit", False))
    return {"is_ok": True, "attempts_left": attempts_left}
