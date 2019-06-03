# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
from app.libs.extensions import db
from app.models.base import Base


class Link(Base):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    tag = db.Column(db.String(10))
    url = db.Column(db.String(255))
