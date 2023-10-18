from flask import make_response, jsonify, request
from config import cfg


def token_required(f):

    def wrapped(*args, **kwargs):

        if 'x-access-token' not in request.headers:
            return make_response(jsonify({"message": "No token"}), 401)

        if request.headers['x-access-token'] != cfg.ACCESS_TOKEN:
            return make_response(jsonify({"message": "Wrong token"}), 403)

        f(*args, **kwargs)

    return wrapped

