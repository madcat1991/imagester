# coding: utf-8
import hashlib
import os
from contextlib import contextmanager

import time
from flask import current_app
from validate_email import validate_email


def get_abs_path(*args):
    """ Concatenates path's parts sent through args and returns the
        absolute path to the file
    """
    return os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), *args))


def check_email(email):
    if email is None:
        return {"is_ok": False, "msg": 'An email address should be specified.'}
    elif not validate_email(email):
        return {"is_ok": False, "msg": 'The email address "%s" is not valid.' % email}

    cnt = current_app.redis.get(email)
    if cnt == '0':
        return {
            "is_ok": False,
            "limit": True,
            "msg": 'Sorry, but the demo version of the application is limited by %s '
                   'suggestion requests per email. We are currently working on this. '
                   'If you would like to help us, please check the "Donation" or "Contact us" sections.'
                   % current_app.config["MAX_REQUESTS_PER_USER"]
        }
    return {"is_ok": True}


def check_images(images):
    allowed_exts = current_app.config['ALLOWED_IMG_EXTENSIONS']

    if not images:
        return {
            "is_ok": False,
            "msg": 'At least one image should be selected'
        }

    for img in images:
        img_ext = img.filename.rsplit('.', 1)[1].lower() if "." in img.filename else None
        if img_ext not in allowed_exts:
            return {
                "is_ok": False,
                "filename": img.filename,
                "msg": 'The file "%s" has an unsupported file type. '
                       'The service only supports the following file types: %s.' %
                       (img.filename, ", ".join(allowed_exts))
            }

        img.seek(0, os.SEEK_END)
        img_bytes = img.tell()
        if img_bytes > current_app.max_image_bytes:
            return {
                "is_ok": False,
                "filename": img.filename,
                "msg": 'The file "%s" exceeds the maximum file size. '
                       'The service only supports images less than %sMB.' %
                       (img.filename, current_app.max_image_bytes / 1024 / 1024)
            }

        # restoring file
        img.seek(0, os.SEEK_SET)
    return {"is_ok": True}


def generate_dir_name(email):
    return hashlib.md5("%s_%s" % (email, time.time())).hexdigest()


def prepare_request(email, utc_offset_minutes, images):
    # add email to redis if does not exist
    with current_app.redis.pipeline() as pipe:
        pipe.set(email, current_app.config["MAX_REQUESTS_PER_USER"], nx=True)
        pipe.sadd("emails", email)
        pipe.execute()

    # get path to save images
    img_dir = generate_dir_name(email)
    img_dir_path = os.path.join(current_app.config['IMG_UPLOAD_DIR'], img_dir)
    os.makedirs(img_dir_path)

    # saving images to folder
    for img in images:
        img.save(os.path.join(img_dir_path, img.filename))

    # saving data to DB
    with get_db_cursor(commit=True) as cur:
        sql = """
            INSERT INTO request (email, utc_offset_minutes, img_dir)
            VALUES (%s, %s, %s)
        """
        cur.execute(sql, (email, utc_offset_minutes, img_dir))

    # reducing the number of attempts
    attempts_left = current_app.redis.decr(email)
    return attempts_left


@contextmanager
def get_db_connection():
    """
    psycopg2 connection context manager.
    Fetch a connection from the connection pool and release it.
    """
    try:
        connection = current_app.pool.getconn()
        yield connection
    finally:
        current_app.pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
    """
    psycopg2 connection.cursor context manager.
    Creates a new cursor and closes it, commiting changes if specified.
    """
    with get_db_connection() as connection:
        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()
