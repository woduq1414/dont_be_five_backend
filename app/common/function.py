import smtplib
import threading
from email.mime.multipart import MIMEMultipart

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import base64
from collections import namedtuple
from flask_restful import Api, Resource, reqparse
from datetime import datetime
# from config import credentials
import requests
from config import DISCORD_WEBHOOK_URL
from flask import request
import ssl

def is_local():
    import socket
    import os

    hostname = socket.gethostname()
    isLocal = None
    if hostname[:7] == "DESKTOP" or hostname[:5] == "Chuns":
        isLocal = True
    else:
        isLocal = False

    return isLocal




def format_url_title(title):
    return title.replace(" ", "-")


def send_discord_webhook(webhook_body):
    requests.post(
        DISCORD_WEBHOOK_URL,
        json=webhook_body)


def get_ip_address():
    return request.headers[
        'X-Forwarded-For'] if 'X-Forwarded-For' in request.headers else request.remote_addr


def send_discord_alert_log(alert_string):

    webhook_body = {

        "embeds": [
            {
                "title": "=========ALERT=========",
                "color": 14177041

            },
            {
                "description" : alert_string
            },
            {
                "fields": [
                    {
                        "name": "URI",
                        "value": request.url,
                        "inline": True
                    },

                ],
                "color": 0

            },

            {
                "title": str(datetime.now()) + ", " + (
                    "로컬에서 발생" if is_local() else "외부에서 발생") + ", " + get_ip_address(),
                "color": 0
            },

        ]
    }
    threading.Thread(target=lambda: send_discord_webhook(webhook_body=webhook_body)).start()


def edit_distance(s1, s2):

        l1, l2 = len(s1), len(s2)
        if l2 > l1:
            return edit_distance(s2, s1)
        if l2 is 0:
            return l1
        prev_row = list(range(l2 + 1))
        current_row = [0] * (l2 + 1)
        for i, c1 in enumerate(s1):
            current_row[0] = i + 1
            for j, c2 in enumerate(s2):
                d_ins = current_row[j] + 1
                d_del = prev_row[j + 1] + 1
                d_sub = prev_row[j] + (1 if c1 != c2 else 0)
                current_row[j + 1] = min(d_ins, d_del, d_sub)
            prev_row[:] = current_row[:]
        return prev_row[-1]





def diff_commonPrefix(text1, text2):
    # Quick check for common null cases.
    if not text1 or not text2 or text1[0] != text2[0]:
        return 0
        # Binary search.
    pointermin = 0
    pointermax = min(len(text1), len(text2))
    pointermid = pointermax
    pointerstart = 0
    while pointermin < pointermid:
        if text1[pointerstart:pointermid] == text2[pointerstart:pointermid]:
            pointermin = pointermid
            pointerstart = pointermin
        else:
            pointermax = pointermid
        pointermid = int((pointermax - pointermin) / 2 + pointermin)
    return pointermid