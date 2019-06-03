# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
import random

from faker import Faker

from app.libs.extensions import db
from app.models import Admin, Category, Comment, Post, Link

faker = Faker('zh_cn')


def fake_admin():
    """Generate admin info"""
    with db.auto_commit():
        admin = Admin(
            username='admin',
            blog_title='测试博客名',
            blog_sub_title='测试副标题',
            name='测试昵称',
            about='测试关于，这个字符串需要稍微长一点，字数补丁...'
        )
        db.session.add(admin)


def fake_category(count=10):
    """Generate post category"""
    with db.auto_commit():
        category = Category(name='默认')
        db.session.add(category)
        for i in range(count):
            category = Category(name=faker.word())
            db.session.add(category)


def fake_posts(count=50):
    """Generate post"""
    with db.auto_commit():
        for i in range(count):
            post = Post(
                title=faker.sentence(),
                body=faker.text(2000),
                category=Category.query.get(random.randint(1, Category.query.count())),
                timestamp=faker.date_time_this_year()
            )
            db.session.add(post)


def fake_comments(count=500):
    """Generate comment"""
    with db.auto_commit():
        # reviewed comments
        for i in range(count):
            comment = Comment(
                author=faker.name(),
                email=faker.email(),
                site=faker.url(),
                body=faker.sentence(),
                timestamp=faker.date_time_this_year(),
                reviewed=True,
                post=Post.query.get(random.randint(1, Post.query.count()))
            )
            db.session.add(comment)

    salt = int(count * 0.1)
    with db.auto_commit():
        # unreviewed comments
        for i in range(salt):
            comment = Comment(
                author=faker.name(),
                email=faker.email(),
                site=faker.url(),
                body=faker.sentence(),
                timestamp=faker.date_time_this_year(),
                reviewed=False,
                post=Post.query.get(random.randint(1, Post.query.count()))
            )
            db.session.add(comment)

    with db.auto_commit():
        # admin comments
        for i in range(salt):
            comment = Comment(
                author='我是管理员',
                email='admin@admin.com',
                site='localhost:5000',
                body=faker.sentence(),
                timestamp=faker.date_time_this_year(),
                from_admin=True,
                reviewed=True,
                post=Post.query.get(random.randint(1, Post.query.count()))
            )
            db.session.add(comment)

    with db.auto_commit():
        # reply comments
        for i in range(salt):
            comment = Comment(
                author=faker.name(),
                email=faker.email(),
                site=faker.url(),
                body=faker.sentence(),
                timestamp=faker.date_time_this_year(),
                reviewed=True,
                replied=Comment.query.get(random.randint(1, Comment.query.count())),
                post=Post.query.get(random.randint(1, Post.query.count()))
            )
            db.session.add(comment)


def fake_links():
    with db.auto_commit():
        weibo = Link(name='Weibo', url='#', tag='weibo')
        weixin = Link(name='Weixin', url='#', tag='weixin')
        douban = Link(name='Douban', url='#', tag='douban')
        zhihu = Link(name='Zhihu', url='#', tag='zhihu')
        github = Link(name='Github', url='#', tag='github')
        twitter = Link(name='Twitter', url='#', tag='twitter')
        facebook = Link(name='FaceBook', url='#', tag='facebook')
        google = Link(name='Google', url='#', tag='google')
        linkedin = Link(name='LinkedIn', url='#', tag='linkedin')
        other = Link(name='Oter', url='#', tag='other')
        telegram = Link(name='Telegram', url='#', tag='telegram')
        frendlink = Link(name='FriendLink', url='#', tag='friendLink')
        db.session.add_all([twitter, facebook, google, linkedin, weibo, weixin,
                            douban, zhihu, github, other, telegram, frendlink])
