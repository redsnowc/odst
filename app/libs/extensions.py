# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
from contextlib import contextmanager

from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_ckeditor import CKEditor
from flask_whooshee import Whooshee
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from flask_wtf import CSRFProtect


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        """
        For SQL rollback
        """
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


db = SQLAlchemy()
moment = Moment()
bootstrap = Bootstrap()
mail = Mail()
ckeditor = CKEditor()
whooshee = Whooshee()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()
debug_toolbar = DebugToolbarExtension()


@login_manager.user_loader
def load_user(user_id):
    from app.models import Admin
    user = Admin.query.get(int(user_id))
    return user


login_manager.login_view = 'web.login'
login_manager.login_message = u'请先登录！'
login_manager.login_message_category = 'warning'
