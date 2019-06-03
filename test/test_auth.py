# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
from flask import url_for

from test.base import BaseTestCase
from app.libs.extensions import db
from app.models import Admin


class AuthTestCase(BaseTestCase):

    def test_login_user(self):
        response = self.login()
        data = response.get_data(as_text=True)
        self.assertIn('欢迎回来 name', data)

    def test_login_fail(self):
        response = self.login(username='wrong', password='wrong-password')
        data = response.get_data(as_text=True)
        self.assertIn('用户名或密码错误', data)

    def test_logout(self):
        self.login()
        response = self.logout()
        data = response.get_data(as_text=True)
        self.assertIn('成功登出', data)

    def test_login_protect(self):
        response = self.client.get(url_for('web.manage_posts'),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('请先登录', data)

    def test_logged_redirect(self):
        self.login()
        response = self.client.get(url_for('web.login'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Learn more', data)

    def test_no_admin_account(self):
        admin = Admin.query.first()
        db.session.delete(admin)
        db.session.commit()
        response = self.login()
        data = response.get_data(as_text=True)
        self.assertIn('管理账户不存在', data)
