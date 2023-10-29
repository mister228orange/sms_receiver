import hashlib

from flask import make_response, jsonify, request
from config import cfg
import logging


def token_required(f):

    def wrapped(*args, **kwargs):
        if 'x-access-token' not in request.headers:
            logging.error("no token")
            return make_response(jsonify({"message": "No token"}), 401)

        token = hashlib.sha256(request.headers['x-access-token'].encode()).hexdigest()
        if token != cfg.ACCESS_TOKEN:
            logging.error("wrong token")
            return make_response(jsonify({"message": "Wrong token"}), 403)

        return f(*args, **kwargs)
    wrapped.__name__ = f.__name__

    return wrapped

