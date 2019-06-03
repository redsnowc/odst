# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
from flask import redirect, url_for, flash, render_template
from flask_login import current_user, login_user, login_required, logout_user

from app.libs.helpers import redirect_back
from app.models import Admin
from app.forms import LoginForm
from app.web import web


@web.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('web.index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.check_password(password):
                login_user(admin, remember)
                flash('欢迎回来 %s' % admin.name, 'success')
                return redirect_back()
            flash('用户名或密码错误', 'warning')
        else:
            flash('管理账户不存在', 'warning')
    return render_template('auth/login.html', form=form)


@web.route('/logout')
@login_required
def logout():
    logout_user()
    flash('成功登出', 'info')
    return redirect_back()
