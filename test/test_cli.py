# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
from flask import current_app

from app.models import Admin, Post, Category, Comment, Link
from app.libs.extensions import db
from test.base import BaseTestCase


class CliTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        db.drop_all()

    def test_forge_commend(self):
        result = self.runner.invoke(args=['forge'])

        self.assertEqual(Admin.query.count(), 1)
        self.assertIn('Generating admin...', result.output)

        self.assertEqual(Category.query.count(), 11)
        self.assertEqual(Category.query.get(1).name, '默认')
        self.assertIn('Generating 10 categories...', result.output)

        self.assertEqual(Post.query.count(), 50)
        self.assertIn('Generating 50 posts', result.output)

        self.assertEqual(Comment.query.count(), 650)
        self.assertIn('Generating 500 comments...', result.output)

        self.assertIn('Generating links...', result.output)
        self.assertIn('Done.', result.output)

        result = self.runner.invoke(args=['forge',
                                          '--category', '5',
                                          '--post', '5',
                                          '--comment', '100'])

        self.assertEqual(Admin.query.count(), 1)
        self.assertIn('Generating admin...', result.output)

        self.assertEqual(Category.query.count(), 6)
        self.assertEqual(Category.query.get(1).name, '默认')
        self.assertIn('Generating 5 categories...', result.output)

        self.assertEqual(Post.query.count(), 5)
        self.assertIn('Generating 5 posts', result.output)

        self.assertEqual(Comment.query.count(), 130)
        self.assertIn('Generating 100 comments...', result.output)

        self.assertIn('Generating links...', result.output)
        self.assertIn('Done.', result.output)

    def test_init(self):
        result = self.runner.invoke(args=['init',
                                          '--username', 'admin',
                                          '--password', '123456789'])
        self.assertIn('Creating the temporary administrator account...',
                      result.output)
        self.assertIn('Create the default category...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(Admin.query.first().username, 'admin')
        self.assertEqual(Category.query.first().name, '默认')

        self.runner.invoke(args=['init',
                                 '--username', 'admin',
                                 '--password', '1234567'])
        result = self.runner.invoke(args=['init',
                                          '--username', 'flask',
                                          '--password', '123456789'])
        self.assertIn('The administrator already exists, updating...',
                      result.output)
        self.assertNotIn('Creating the temporary administrator account...',
                         result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(Admin.query.first().username, 'flask')
        self.assertEqual(Category.query.first().name, '默认')

    def test_initdb(self):
        result = self.runner.invoke(args=['initdb'])
        self.assertIn('Initialized database.', result.output)

        result = self.runner.invoke(args=['initdb', '--drop'], input='y\n')
        self.assertIn('This operation will delete the database, do you want to continue?',
                      result.output)
        self.assertIn('Tables was removed successfully.', result.output)

