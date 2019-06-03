# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
import unittest

from flask import url_for

from app import create_app
from app.libs.extensions import db
from app.models import Admin


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app(config='testing')
        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

        db.create_all()
        admin = Admin(
            username='admin',
            blog_title='Test title',
            blog_sub_title='Test sub title',
            name='name',
            about='about'
        )
        admin.set_password('12345678')
        db.session.add(admin)
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.context.pop()

    def login(self, username=None, password=None):
        if username is None and password is None:
            username = 'admin'
            password = '12345678'

        return self.client.post(url_for('web.login'), data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('web.logout'), follow_redirects=True)
