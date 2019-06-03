"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
from flask import Blueprint

web = Blueprint('web', __name__)


from app.web import blog
from app.web import auth
from app.web import admin
