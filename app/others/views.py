import marshmallow
from flask import Blueprint, make_response
from flask import Flask, render_template, session, request, flash, redirect, url_for, Response, abort, jsonify, \
    send_file
import socket
import os
import random
import copy
# from app.global_var import munhak_rows_data
from flask_sqlalchemy import SQLAlchemy, Model

import json
import base64
from collections import namedtuple
from flask_restful import Api, Resource, reqparse

from app.common.decorator import return_500_if_errors
from app.db import *
from config import SECRET_KEY
from app.cache import cache
import time
from config import SECRET_KEY
from marshmallow import Schema, fields, pprint, validate
from datetime import datetime
from sqlalchemy import func, desc
import hashlib

others_bp = Blueprint('others', __name__)


@others_bp.route('/images/<path:path>')
def get_image(path):
    def get_absolute_path(path):
        import os
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = path
        abs_file_path = os.path.join(script_dir, rel_path)
        return abs_file_path

    return send_file(
        get_absolute_path(f"../../images/{path}"),
        mimetype='image/png',
        attachment_filename='snapshot.png',
        cache_timeout=0
    )


@others_bp.route("/api/save-data/restore")
def save_data_restore():
    resp = make_response(render_template("index_new.html"))
    resp.set_cookie('PJAX-URL', base64.b64encode(request.url.encode("UTF-8")), max_age=None, expires=None, path='/')
    return resp


@others_bp.route("/api/save-data/save", methods=["GET", "POST"])
def save_data_save():
    args = request.get_json()
    print(args)


@others_bp.route("/api/custom-level/list", methods=["GET", "POST"])
def get_custom_level_list():
    args = request.get_json()
    try:
        data = GetLevelDataListSchema().load(args)
    except marshmallow.exceptions.ValidationError as e:
        return abort(400)

    if "type" in data and "query" in data:
        if data["type"] == "맵 이름":
            custom_level_rows = CustomLevel.query.filter_by(is_public=True).filter(
                CustomLevel.title.like(f"%{data['query']}%")).order_by(
        desc("level_seq")).limit(
                10).offset(
                10 * (data["page"])).all()
        elif data["type"] == "맵 코드":
            custom_level_rows = CustomLevel.query.filter_by( level_id=data["query"]).order_by(
        desc("level_seq")).limit(
                10).offset(
                10 * (data["page"])).all()



    else:
        if "type" in data and data["type"] == "my":
            print("SFD")
            custom_level_rows = CustomLevel.query.filter_by(maker_device_id=data["device_id"]).order_by(
                desc("level_seq")).limit(
                10).offset(
                10 * (data["page"])).all()
        else:
            custom_level_rows = CustomLevel.query.filter_by(is_public=True).order_by(
            desc("level_seq")).limit(
                10).offset(
                10 * (data["page"])).all()

    # time.sleep(1)
    # custom_level_rows = reversed(custom_level_rows)



    return jsonify(
        {"data": [
            {"levelId": custom_level_row.level_id, "addDate": custom_level_row.add_date, "isMine" : custom_level_row.maker_device_id == data["device_id"],
             "levelData": custom_level_row.level_data, "title": custom_level_row.title} for custom_level_row in
            custom_level_rows
        ]}

    )




@others_bp.route("/api/custom-level/delete", methods=["GET", "POST"])
def delete_custom_level_list():
    args = request.get_json()
    try:
        data = DeleteLevelDataSchema().load(args)
    except marshmallow.exceptions.ValidationError as e:
        return abort(400)


    target_row = CustomLevel.query.filter_by(level_id = data["level_id"], maker_device_id =data["device_id"]).first()
    if target_row is not None:
        db.session.delete(target_row)
        db.session.commit()



    return jsonify(
        {"message" : "success"}

    )




@others_bp.route("/api/custom-level/upload", methods=["GET", "POST"])
def custom_level_upload():
    args = request.get_json()
    try:
        data = UploadLevelDataSchema().load(args)
    except marshmallow.exceptions.ValidationError as e:
        return abort(400)

    rnd_string = get_random_string()
    while True:

        if CustomLevel.query.filter_by(level_id=rnd_string).first() is not None:

            print(rnd_string)
            continue
        else:
            break

    custom_level = CustomLevel(
        add_date=datetime.now(),
        maker_device_id=data["device_id"],
        app_version=data["app_version"],
        title=data["title"],
        level_id=get_random_string(),
        level_data=data["level_data"],
        is_public=data["is_public"]
    )

    db.session.add(custom_level)
    db.session.commit()
    # time.sleep(5)
    return jsonify({
        "message": "success"
    })


class UploadLevelDataSchema(Schema):
    device_id = fields.String(required=True, validate=validate.Regexp(r'^.{1,301}$'))
    app_version = fields.String(required=True, validate=validate.Regexp(r'^.{1,301}$'))
    title = fields.String(required=True, validate=validate.Regexp(r'^.{1,30}$'))
    level_data = fields.Raw(required=True)
    is_public = fields.Boolean(required=True)


class GetLevelDataListSchema(Schema):
    page = fields.Integer(required=True)

    type = fields.String(required=False)
    query = fields.String(required=False)

    device_id = fields.String(required=True)



class DeleteLevelDataSchema(Schema):

    level_id = fields.String(required=True)

    device_id = fields.String(required=True)


# def data_to_packet:
#     hashlib.sha256(
import string
import random


def get_random_string():
    letters = [x for x in string.ascii_uppercase if x != "D"]
    return ''.join(random.choice(letters) for i in range(5))
