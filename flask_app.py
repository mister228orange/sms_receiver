from flask import Flask, request, Response
import json
import logging
from utils import token_required
from DB_Manager import DB_manager
from flask_cors import CORS



app = Flask(__name__)
CORS(app)
db = DB_manager()


@app.route('/sms', methods = ['POST'])
@token_required
def receive_sms():
    sms = request.get_json()
    db.handle_msg(sms)
    return Response("Success", status=202)


@app.route('/get_all_sms', methods = ['GET'])
@token_required
def show_sms():
    src = request.args.get('src')
    sms_list = db.get_all_sms(src)

    return {
            "sms": sms_list
        }


@app.route('/get_new_sms', methods = ['GET'])
@token_required
def show_new_sms():
    unviewed_sms = db.get_new_sms()

    return {
            "new_sms": unviewed_sms
        }


@app.route('/mark_as_read', methods = ['POST'])
@token_required
def update_statuses():
    logging.error(request.get_json())
    sms_ids = request.get_json()["sms_ids"]
    try:
        db.mark_as_read(sms_ids)
        return Response("Success", status=202)
    except:
        return Response("Something went wrong", status=500)


@app.route('/get_incorrect_sms', methods = ['GET'])
#@token_required
def show_incorrect_sms():
    incorrect_sms = db.get_incorrect_sms()

    return {
            "new_sms": incorrect_sms
        }


@app.route('/delete_read_sms', methods = ['DELETE'])
@token_required
def delete_read_sms():
    try:
        db.delete_read_sms()
        return Response("Success", status=200)
    except:
        return Response("Something went wrong", status=500)


