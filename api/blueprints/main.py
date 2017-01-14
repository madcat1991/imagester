# coding: utf-8

import logging

from flask import Blueprint
from flask import current_app
from flask import request


from api.exceptions import ArgErrorException
from api.functions import check_email, check_images, prepare_request

main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)


@main.route('/ping/')
def ping_handler():
    """Ping-pong command
    """
    return {"result": "pong"}


@main.route('/check_email/')
def check_email_handler():
    email = request.args.get("email")
    return check_email(email)


@main.route('/upload/', methods=["POST"])
def upload_handler():
    email = request.form.get("email")
    email_check_res = check_email(email)

    utc_offset_minutes = request.form.get("offset_minutes", type=int, default=0)

    if email_check_res["is_ok"]:
        images = request.files.getlist("images")[: current_app.config["MAX_IMAGES_PER_REQUEST"]]
        images_check_res = check_images(images)

        if images_check_res["is_ok"]:
            attempts_left = prepare_request(email, utc_offset_minutes, images)
        else:
            raise ArgErrorException(
                "images", images_check_res["msg"], filename=images_check_res["filename"]
            )
    else:
        raise ArgErrorException("email", email_check_res["msg"])
    return {"is_ok": True, "attempts_left": attempts_left}
