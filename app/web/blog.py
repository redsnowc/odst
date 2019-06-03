# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
from flask import render_template, flash, current_app, request, url_for, \
    redirect
from flask_login import current_user

from app import db
from app.forms import AdminCommentForm, CommentForm
from app.libs.emails import send_mail
from app.libs.helpers import redirect_back
from app.models import Post, Category, Comment
from app.web import web


@web.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_POST_PER_PAGE']
    pagination = Post.query.order_by(
        Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template(
        'blog/index.html', pagination=pagination, posts=posts)


@web.route('/about')
def about():
    return render_template('blog/about.html')


@web.route('/post/<int:post_id>', methods=['POST', 'GET'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).filter_by(
        reviewed=True).order_by(Comment.timestamp.asc()).paginate(page,
                                                                  per_page)
    comments = pagination.items

    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['BLOG_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    if form.validate_on_submit():
        with db.auto_commit():
            author = form.author.data
            email = form.email.data
            site = form.email.data
            body = form.body.data
            comment = Comment(
                author=author, email=email, site=site, body=body,
                from_admin=from_admin, post=post, reviewed=reviewed
            )
            replied_id = request.args.get('reply')
            if replied_id:
                replied_comment = Comment.query.get_or_404(replied_id)
                comment.replied = replied_comment
                send_mail('评论有新的回复', replied_comment.email,
                          'email/send_new_reply.html', comment=replied_comment)
            db.session.add(comment)
        if current_user.is_authenticated:
            flash('评论发表成功！', 'success')
        else:
            flash('感谢您的评论，评论将在审核后发表', 'info')
            send_mail('新的评论', current_app.config['BLOG_EMAIL'],
                      'email/send_new_comment.html', post=post)
        return redirect(url_for('web.show_post', post_id=post.id))
    return render_template('blog/post.html', post=post, pagination=pagination,
                           comments=comments, form=form)


@web.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('评论已关闭', 'warning')
        return redirect(url_for('web.show_post', post_id=comment.post.id))
    return redirect(url_for(
        '.show_post', post_id=comment.post_id, reply=comment_id,
        author=comment.author) + '#comment-form')


@web.route('/category/<name>')
def show_category(name):
    category = Category.query.filter_by(name=name).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(
        Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category,
                           pagination=pagination, posts=posts)


@web.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if q == '':
        flash('搜索内容不能为空', 'warning')
        return redirect_back()

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_SEARCH_PER_PAGE']
    pagination = Post.query.whooshee_search(q).order_by(
        Post.timestamp.desc()).paginate(page, per_page)
    results = pagination.items

    if not results:
        flash('没有搜索到任何包含 “%s” 的结果' % q, 'warning')

    return render_template(
        'blog/search.html', q=q, results=results, pagination=pagination)
