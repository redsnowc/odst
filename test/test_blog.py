# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
from flask import url_for

from app.models import Category, Post, Comment, Link
from app.libs.extensions import db
from test.base import BaseTestCase


class BlogTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.login()

        category = Category(name='默认')
        post = Post(title='post title', category=category, body='post body')
        comment_admin = Comment(body='admin comment', post=post,
                                from_admin=True, reviewed=True)
        comment_guest = Comment(author='guest', post=post, body='guest comment',
                                from_admin=False, reviewed=True)
        comment_unread = Comment(author='unread', post=post, from_admin=False,
                                 body='unread comment', reviewed=False)
        link = Link(name='link', tag='other', url='https://www.google.com')
        friend_link = Link(name='friend_link', tag='friendLink',
                           url='https://github.com')
        db.session.add_all([category, post, comment_admin, comment_guest,
                            comment_unread, link, friend_link])
        db.session.commit()

    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('首页', data)
        self.assertIn('关于', data)
        self.assertIn('新增', data)
        self.assertIn('管理', data)
        self.assertIn('New', data)
        self.assertIn('Test title', data)
        self.assertIn('Test sub title', data)
        self.assertIn('name', data)
        self.assertIn('post title', data)
        self.assertIn('文章分类', data)
        self.assertIn('默认', data)
        self.assertIn('个人链接', data)
        self.assertIn('link', data)
        self.assertIn('友情链接', data)
        self.assertIn('friend_link', data)
        self.assertIn('登出', data)
        self.assertIn('2019', data)

    def test_none_logged_index_page(self):
        self.logout()
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('新增', data)
        self.assertNotIn('管理', data)
        self.assertIn('登陆', data)

    def test_post_page(self):
        response = self.client.get(url_for('web.show_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('post title', data)
        self.assertIn('post body', data)
        self.assertIn('编辑', data)
        self.assertIn('删除', data)
        self.assertIn('关闭评论', data)

    def test_about_page(self):
        response = self.client.get(url_for('web.about'))
        data = response.get_data(as_text=True)
        self.assertIn('about', data)

    def test_category_page(self):
        response = self.client.get(url_for('web.show_category', name='默认'))
        data = response.get_data(as_text=True)
        self.assertIn('默认', data)
        self.assertIn('post title', data)

    def test_new_admin_comment(self):
        response = self.client.post(url_for('web.show_post', post_id=1),
                                    data=dict(body='new admin comment',
                                              post=Post.query.get(1)),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('评论发表成功', data)
        self.assertIn('new admin comment', data)

    def test_new_guest_comment(self):
        self.logout()
        response = self.client.post(url_for('web.show_post', post_id=1),
                                    data=dict(author='guest',
                                              email='guest@guest.com',
                                              site='https://guest.com',
                                              body='new guest comment',
                                              post=Post.query.get(1)),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('感谢您的评论，评论将在审核后发表', data)
        self.assertNotIn('new guest comment', data)

    def test_reply_status(self):
        response = self.client.get(url_for('web.reply_comment', comment_id=1),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('回复', data)
        self.assertIn('取消', data)

        post = Post.query.get(1)
        post.can_comment = False
        db.session.commit()

        response = self.client.get(url_for('web.reply_comment', comment_id=1),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('评论已关闭', data)
        self.assertNotIn('alert alert-dark', data)
        self.assertNotIn('取消', data)

    def test_new_admin_reply(self):
        response = self.client.post(url_for('web.show_post', post_id=1)
                                    + '?reply=1', data=dict(
            body='admin reply comment',
            post=Post.query.get(1)
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('评论发表成功', data)
        self.assertIn('admin reply comment', data)
        self.assertIn('badge badge-light', data)

    def test_new_guest_reply(self):
        self.logout()
        response = self.client.post(url_for('web.show_post', post_id=1)
                                    + '?reply=1', data=dict(
            author='guest',
            email='guest@guest.com',
            site='https://guest.com',
            body='guest reply comment',
            post=Post.query.get(1)
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('感谢您的评论，评论将在审核后发表', data)
        self.assertNotIn('guest reply comment', data)

    def test_search(self):
        response = self.client.get(url_for('web.search') + '?q= ',
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('搜索内容不能为空', data)

        response = self.client.get(url_for('web.search') + '?q=post',
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('title', data)

        response = self.client.get(url_for('web.search') + '?q=nothing',
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('没有搜索到任何包含', data)

    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn('nothing could be found...', data)
