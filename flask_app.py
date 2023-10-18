from flask import Flask, request, Response
import json
import logging
import os
from DB_Manager import DB_manager



app = Flask(__name__)
db = DB_manager()
bucket = []

@app.route('/sms', methods = ['POST'])
def receive_sms():
    sms = request.get_json()
    bucket.append(sms)
    db.handle_msg(sms)
    return Response("Success", status=202)


@app.route('/sms', methods = ['GET'])
def show_sms():
    unviewed_sms = db.get_new_sms()

    return {
            "new_sms": unviewed_sms
        }