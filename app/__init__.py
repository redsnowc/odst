# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
import secrets

import click
# import sentry_sdk

from flask import Flask, render_template
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from flask_wtf.csrf import CSRFError
# from sentry_sdk.integrations.flask import FlaskIntegration

from app.configs import configs
from app.libs.extensions import db, moment, bootstrap, mail, ckeditor, whooshee, \
    login_manager, csrf, debug_toolbar, migrate
from app.libs.fakers import fake_links
from app.models import Admin, Category, Comment, Link

"""
sentry_sdk.init(
    dsn="write here",
    integrations=[FlaskIntegration()]
)
"""


def create_app(config='development'):
    app = Flask(__name__)
    app.config.from_object(configs[config])
    register_blueprints(app)
    register_commands(app)
    register_extensions(app)
    register_template_context(app)
    register_errors(app)
    register_request_handler(app)
    return app


def register_blueprints(app):
    from app.web import web
    app.register_blueprint(web)


def register_extensions(app):
    db.init_app(app)
    moment.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    ckeditor.init_app(app)
    whooshee.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    debug_toolbar.init_app(app)


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(admin=admin, categories=categories,
                    unread_comments=unread_comments, links=links, Link=Link)


def register_commands(app):
    @app.cli.command()
    @click.option('--category', default=10,
                  help='Quantity of categories, default is 10.')
    @click.option('--post', default=50,
                  help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500,
                  help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        """
        Generate test data
        """
        from app.libs.fakers import fake_admin, fake_category, fake_comments, \
            fake_posts

        db.drop_all()
        db.create_all()

        click.echo('Generating admin...')
        fake_admin()

        click.echo('Generating %d categories...' % category)
        fake_category(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        click.echo('Generating %s comments...' % comment)
        fake_comments(comment)

        click.echo('Generating links...')
        fake_links()

        click.echo('Done.')

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='This password used to login')
    def init(username, password):
        """
        Init Admin account
        """
        click.echo('Initializing Database...')
        db.create_all()

        admin = Admin.query.first()
        with db.auto_commit():
            if admin:
                click.echo('The administrator already exists, updating...')
                admin.username = username
                admin.set_password(password)
            else:
                click.echo('Creating the temporary administrator account...')
                admin = Admin(
                    username=username,
                    blog_title='临时博客名',
                    blog_sub_title='临时副标题',
                    name='临时昵称',
                    about='临时关于'
                )
                admin.set_password(password)
                db.session.add(admin)

            category = Category.query.first()
            if category is None:
                click.echo('Create the default category...')
                category = Category(name='默认')
                db.session.add(category)
        click.echo('Done.')

    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """
        Initialize the database
        """
        if drop:
            click.confirm(
                'This operation will delete the database, do you want to continue?',
                abort=True)
            db.drop_all()
            click.echo('Tables was removed successfully.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--mail_server', prompt=True, help='Mail server address')
    @click.option('--mail_username', prompt=True, help='Mail server username')
    @click.option('--mail_password', prompt=True, help='Mail server password')
    @click.option('--admin_email', prompt=True, help='Admin Email address')
    @click.option('--mysql', is_flag=True, help='Use MySQL database.')
    def initenv(mail_server, mail_username, mail_password, admin_email, mysql):
        """
        Generate .env file for sensitive information
        """
        secret_key = secrets.token_urlsafe(32)
        if mysql:
            mysql_password = input('MySQL password:')
            with open('.env', 'w') as f:
                f.write('MAIL_SERVER=' + "'" + mail_server + "'" + '\n'
                        'MAIL_USERNAME=' + "'" + mail_username + "'" + '\n'
                        'MAIL_PASSWORD=' + "'" + mail_password + "'" + '\n'
                        'BLOG_EMAIL=' + "'" + admin_email + "'" + '\n'
                        'SECRET_KEY=' + "'" + secret_key + "'" + '\n'
                        'DATABASE_URI=' + "'mysql+cymysql://root:" + mysql_password + "@localhost/blog'")
        else:
            with open('.env', 'w') as f:
                f.write('MAIL_SERVER=' + "'" + mail_server + "'" + '\n'
                        'MAIL_USERNAME=' + "'" + mail_username + "'" + '\n'
                        'MAIL_PASSWORD=' + "'" + mail_password + "'" + '\n'
                        'BLOG_EMAIL=' + "'" + admin_email + "'" + '\n'
                        'SECRET_KEY=' + "'" + secret_key + "'")
        click.echo('Creating .env file...')
        click.echo('Done.')


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error/500.html'), 500

    @app.errorhandler(CSRFError)
    def handel_csrf_error(e):
        return render_template('error/400.html'), 400


def register_request_handler(app):
    @app.after_request
    def query_profiler(response):
        for q in get_debug_queries():
            if q.duration >= app.config['BLOG_SLOW_QUERY_THRESHOLD']:
                app.logger.warning(
                    'Slow query: Duration: %fs\n Context: %s\nQuery: %s\n'
                    % (q.duration, q.context, q.statement)
                )
        return response
