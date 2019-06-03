# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
from threading import Thread

from flask import url_for, current_app, render_template
from flask_mail import Message

from app.libs.extensions import mail


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_mail(subject, to, template, **kwargs):
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to])
    message.html = render_template(template, **kwargs)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
