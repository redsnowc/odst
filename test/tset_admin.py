# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
import io

from flask import url_for

from app.models import Post, Category, Comment, Link
from app.libs.extensions import db
from test.base import BaseTestCase


class AdminTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.login()

        category = Category(name='默认')
        post = Post(title='Post', category=category, body='post body')
        comment = Comment(body='comment body', post=post, from_admin=True,
                          reviewed=True)
        link = Link(name='link', tag='other', url='https://link.com')
        db.session.add_all([category, post, comment, link])
        db.session.commit()

    def test_manage_posts(self):
        response = self.client.get(url_for('web.manage_posts'))
        data = response.get_data(as_text=True)
        self.assertIn('Post', data)
        self.assertIn('默认', data)

    def test_new_post(self):
        response = self.client.get(url_for('web.new_post'))
        data = response.get_data(as_text=True)
        self.assertIn('标题', data)
        self.assertIn('正文', data)

        response = self.client.post(url_for('web.new_post'), data=dict(
            title='new post',
            category=1,
            body='new body'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('文章发布成功', data)
        self.assertIn('new post', data)
        self.assertIn('new body', data)

    def test_edit_post(self):
        response = self.client.get(url_for('web.edit_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('Post', data)
        self.assertIn('post body', data)

        response = self.client.post(url_for('web.edit_post', post_id=1), data=dict(
            title='edit post',
            category=1,
            body='edit post body'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('文章更新成功', data)
        self.assertIn('edit post', data)
        self.assertIn('edit post body', data)

    def test_delete_post(self):
        response = self.client.get(url_for('web.delete_post', post_id=1),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('文章已删除', data)
        self.assertIn('405 Method Not Allowed', data)

        response = self.client.post(url_for('web.delete_post', post_id=1),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('文章已删除', data)

    def test_manage_categories(self):
        response = self.client.get(url_for('web.manage_categories'))
        data = response.get_data(as_text=True)
        self.assertIn('默认', data)
        self.assertIn('文章数量', data)

    def test_new_category(self):
        response = self.client.get(url_for('web.new_category'))
        data = response.get_data(as_text=True)
        self.assertIn('名称', data)

        response = self.client.post(url_for('web.new_category'), data=dict(
            name='new category'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('分类创建成功', data)
        self.assertIn('new category', data)

        response = self.client.post(url_for('web.new_category', data=dict(
            name='默认'
        )))
        data = response.get_data(as_text=True)
        self.assertIn('invalid-feedback', data)

        category = Category.query.get(1)
        post = Post(title='test title', body='test_body', category=category)
        db.session.add(post)
        db.session.commit()
        response = self.client.get(url_for('web.show_category',
                                           name=category.name))
        data = response.get_data(as_text=True)
        self.assertIn('test title', data)

    def test_edit_category(self):
        category = Category(name='Python')
        db.session.add(category)
        db.session.commit()
        response = self.client.get(url_for('web.edit_category', category_id=2))
        data = response.get_data(as_text=True)
        self.assertIn('Python', data)
        self.assertIn('提交', data)

        response = self.client.get(url_for('web.edit_category', category_id=1),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('默认分类不能修改', data)

        response = self.client.post(url_for('web.edit_category', category_id=1),
                                    data=dict(name='edit 1'),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('默认分类不能修改', data)
        self.assertNotIn('更新成功', data)
        self.assertNotIn('edit 1', data)

        response = self.client.post(url_for('web.edit_category', category_id=2),
                                    data=dict(name='flask edit'),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Python', data)
        self.assertIn('flask edit', data)

    def test_delete_category(self):
        category = Category(name='python')
        post = Post(title='flask', body='body', category=category)
        db.session.add_all([category, post])
        db.session.commit()

        response = self.client.get(url_for('web.delete_category',
                                           category_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('分类删除成功', data)
        self.assertIn('405 Method Not Allowed', data)

        response = self.client.post(url_for('web.delete_category',
                                            category_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('分类删除成功', data)
        self.assertIn('默认分类不能删除', data)
        self.assertIn('默认', data)

        response = self.client.post(url_for('web.delete_category',
                                            category_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('分类删除成功', data)
        self.assertNotIn('python', data)
        self.assertIn('默认', data)

        response = self.client.get(url_for('web.show_category', name='默认'))
        data = response.get_data(as_text=True)
        self.assertIn('flask', data)
        self.assertIn('2', data)

    def test_manage_comments(self):
        comment = Comment(author='guest', email='guest@guest.com',
                          body='guest comment', post=Post.query.get(1))
        db.session.add(comment)
        db.session.commit()
        response = self.client.get(url_for('web.manage_comments', filter='all'))
        data = response.get_data(as_text=True)
        self.assertIn('作者', data)
        self.assertIn('发布', data)

        response = self.client.get(url_for('web.manage_comments', filter='unread'))
        data = response.get_data(as_text=True)
        self.assertIn('发布', data)
        self.assertNotIn('作者', data)

        response = self.client.get(url_for('web.manage_comments', filter='admin'))
        data = response.get_data(as_text=True)
        self.assertNotIn('发布', data)
        self.assertIn('作者', data)

    def test_delete_comment(self):
        response = self.client.get(url_for('web.delete_comment', comment_id=1),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('评论已删除', data)
        self.assertIn('405 Method Not Allowed', data)

        response = self.client.post(url_for('web.delete_comment', comment_id=1),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('评论已删除', data)
        self.assertNotIn('comment body', data)

    def test_enable_comment(self):
        post = Post.query.get(1)
        post.can_comment = False
        db.session.commit()

        response = self.client.post(url_for('web.set_comment', post_id=1),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('评论已开启', data)

        response = self.client.get(url_for('web.show_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('<div id="comment-form">', data)

    def test_disable_comment(self):
        response = self.client.post(url_for('web.set_comment', post_id=1),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('评论已关闭', data)

        response = self.client.get(url_for('web.show_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertNotIn('<div id="comment-form">', data)

    def test_approve_comment(self):
        self.logout()
        response = self.client.post(url_for('web.show_post', post_id=1), data=dict(
            author='guest',
            email='guest@guest.com',
            site='https://guest.com',
            body='unread comment',
            post=Post.query.get(1)
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('感谢您的评论，评论将在审核后发表', data)
        self.assertNotIn('unread comment', data)

        self.login()
        response = self.client.post(url_for('web.approve_comment', comment_id=2),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('评论审核成功', data)

    def test_manage_links(self):
        response = self.client.get(url_for('web.manage_links'))
        data = response.get_data(as_text=True)
        self.assertIn('other', data)
        self.assertIn('link', data)

    def test_new_link(self):
        response = self.client.get(url_for('web.new_link'))
        data = response.get_data(as_text=True)
        self.assertIn('链接描述', data)
        self.assertIn('地址', data)
        self.assertIn('标签', data)

        response = self.client.post(url_for('web.new_link'), data=dict(
            name='Github',
            url='https://github.com',
            tag='github'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('添加链接成功', data)
        self.assertIn('Github', data)

        response = self.client.get(url_for('web.index'))
        data = response.get_data(as_text=True)
        self.assertIn('Github', data)
        self.assertIn('href="#icongithub"', data)

    def test_edit_link(self):
        response = self.client.get(url_for('web.edit_link', link_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('link', data)
        self.assertIn('https://link.com', data)
        self.assertIn('other', data)

        response = self.client.post(url_for('web.edit_link', link_id=1), data=dict(
            name='Github',
            url='https://github.com',
            tag='github'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('链接更新成功', data)
        self.assertIn('Github', data)
        self.assertIn('https://github.com', data)
        self.assertIn('github', data)
        self.assertNotIn('https://link.com', data)

    def test_delete_link(self):
        response = self.client.get(url_for('web.delete_link', link_id=1),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('链接删除成功', data)
        self.assertIn('405 Method Not Allowed', data)

        response = self.client.post(url_for('web.delete_link', link_id=1),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('链接删除成功', data)
        self.assertNotIn('https://link.com', data)

    def test_manage_settings(self):
        response = self.client.get(url_for('web.manage_settings'))
        data = response.get_data(as_text=True)
        self.assertIn('Test title', data)
        self.assertIn('Test sub title', data)
        self.assertIn('about', data)
        self.assertIn('darkly', data)

        response = self.client.post(url_for('web.manage_settings'), data=dict(
            blog_title='edit title',
            blog_sub_title='edit sub title',
            name='edit name',
            about='edit about'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('博客设置成功', data)
        self.assertIn('edit name', data)

    def test_upload(self):
        data = {'blog_index_image': (io.BytesIO(b"test"), 'test.png')}
        response = self.client.post(url_for('web.manage_settings'), data=data,
                                    follow_redirects=True,
                                    content_type='multipart/form-data')
        data = response.get_data(as_text=True)
        self.assertIn('仅支持 JPG', data)

    def test_change_theme(self):
        response = self.client.post(url_for('web.manage_settings'), data=dict(
            blog_title='blog title',
            blog_sub_title='sub title',
            name='name',
            about='about',
            theme='lux'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('lux.css', data)
