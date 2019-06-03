# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
import os

from flask import render_template, request, current_app, flash, redirect, \
    url_for, send_from_directory
from flask_ckeditor import upload_fail, upload_success
from flask_login import login_required

from app.libs.extensions import db
from app.forms import PostForm, CategoryForm, LinkForm, BlogSettingForm
from app.libs.helpers import allowed_file, redirect_back, upload_file
from app.models import Post, Category, Comment, Link, Admin
from app.web import web


@web.route('/manage/posts')
@login_required
def manage_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_MANAGE_POST_PER_PAGE']
    )
    posts = pagination.items
    return render_template('admin/manage_posts.html', pagination=pagination,
                           posts=posts)


@web.route('/new/post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        with db.auto_commit():
            post = Post(title=title, body=body, category=category)
            db.session.add(post)
        flash('文章发布成功', 'success')
        return redirect(url_for('web.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)


@web.route('/edit/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        with db.auto_commit():
            post.title = form.title.data
            post.body = form.body.data
            post.category = Category.query.get(form.category.data)
        flash('文章更新成功', 'success')
        return redirect(url_for('web.show_post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('admin/edit_post.html', form=form)


@web.route('/delete/post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    with db.auto_commit():
        db.session.delete(post)
    flash('文章已删除', 'info')
    return redirect_back()


@web.route('/manage/categories')
@login_required
def manage_categories():
    return render_template('admin/manage_categories.html')


@web.route('/new/category', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        with db.auto_commit():
            name = form.name.data
            db.session.add(Category(name=name))
        flash('分类创建成功', 'success')
        return redirect(url_for('web.manage_categories'))
    return render_template('admin/new_category.html', form=form)


@web.route('/edit/category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    form = CategoryForm()
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('默认分类不能修改！', 'warning')
        return redirect(url_for('web.index'))
    if form.validate_on_submit():
        with db.auto_commit():
            category.name = form.name.data
        flash('分类更新成功', 'success')
        return redirect(url_for('web.manage_categories'))
    form.name.data = category.name
    return render_template('admin/edit_category.html', form=form)


@web.route('/delete/category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('默认分类不能删除！', 'warning')
        return redirect(url_for('web.index'))
    category.delete()
    flash('分类删除成功', 'info')
    return redirect(url_for('web.manage_categories'))


@web.route('/manage/comments/<any(all, unread, admin):filter>')
@login_required
def manage_comments(filter):
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_COMMENT_PER_PAGE']
    if filter == 'all':
        filtered_comments = Comment.query
    elif filter == 'unread':
        filtered_comments = Comment.query.filter_by(reviewed=False)
    else:
        filtered_comments = Comment.query.filter_by(from_admin=True)

    pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=per_page
    )
    comments = pagination.items
    return render_template('admin/manage_comments.html', comments=comments,
                           pagination=pagination)


@web.route('/delete/comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    with db.auto_commit():
        db.session.delete(comment)
    flash('评论已删除', 'info')
    return redirect_back()


@web.route('/approve/comment/<int:comment_id>', methods=['POST'])
@login_required
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    with db.auto_commit():
        comment.reviewed = True
    flash('评论审核成功', 'success')
    return redirect_back()


@web.route('/set-comment/<int:post_id>', methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    with db.auto_commit():
        if post.can_comment:
            post.can_comment = False
            flash('评论已关闭', 'info')
        else:
            post.can_comment = True
            flash('评论已开启', 'info')
    return redirect(url_for('web.show_post', post_id=post.id))


@web.route('/manage/links')
@login_required
def manage_links():
    return render_template('admin/manage_links.html')


@web.route('/new/link', methods=['GET', 'POST'])
@login_required
def new_link():
    form = LinkForm()
    if form.validate_on_submit():
        with db.auto_commit():
            link = Link()
            link.set__attrs(form.data)
            db.session.add(link)
        flash('添加链接成功', 'success')
        return redirect(url_for('web.manage_links'))
    return render_template('admin/new_link.html', form=form)


@web.route('/edit/link/<int:link_id>', methods=['GET', 'POST'])
@login_required
def edit_link(link_id):
    form = LinkForm()
    link = Link.query.get_or_404(link_id)
    if form.validate_on_submit():
        with db.auto_commit():
            link.set__attrs(form.data)
            db.session.add(link)
        flash('链接更新成功！', 'success')
        return redirect(url_for('web.manage_links'))
    form.name.data = link.name
    form.tag.data = link.tag
    form.url.data = link.url
    return render_template('admin/edit_link.html', form=form)


@web.route('/delete/link/<int:link_id>', methods=['POST'])
@login_required
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    with db.auto_commit():
        db.session.delete(link)
    flash('链接删除成功', 'info')
    return redirect_back()


@web.route('/manage/settings', methods=['GET', 'POST'])
@login_required
def manage_settings():
    form = BlogSettingForm()
    admin = Admin.query.first()
    if form.validate_on_submit():
        with db.auto_commit():
            admin.set__attrs(form.data)
            db.session.add(admin)

        f = form.blog_index_image.data
        if f:
            upload_file(f, 'index_image')
        flash('博客设置成功', 'success')
        return redirect_back()

    form.blog_title.data = admin.blog_title
    form.blog_sub_title.data = admin.blog_sub_title
    form.name.data = admin.name
    form.about.data = admin.about
    form.theme.data = admin.theme
    return render_template('admin/manage_settings.html', form=form)


@web.route('/uploads/<path:filename>')
def get_image(filename):
    return send_from_directory(current_app.config['BLOG_UPLOAD_PATH'], filename)


@web.route('/upload', methods=['POST'])
def upload_image():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail('仅支持上传图片！')
    f.save(os.path.join(current_app.config['BLOG_UPLOAD_PATH'], f.filename))
    url = url_for('.get_image', filename=f.filename)
    return upload_success(url, f.filename)


# @web.route('/sentry')
# def trigger_error():
#     division_by_zero = 1 / 0
