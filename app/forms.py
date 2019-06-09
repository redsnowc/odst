# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, \
    SelectField, HiddenField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, Optional, Email, URL, \
    ValidationError

from app.models.category import Category


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 20, message='用户名由 1 - 20个字符组成')])
    password = PasswordField('密码', validators=[
        DataRequired(), Length(8, 128, message='密码由 8 - 128 个字符组成')])
    remember = BooleanField('记住我')
    submit = SubmitField('登陆')


class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 60)])
    category = SelectField('分类', coerce=int, default=1)
    body = CKEditorField('正文', validators=[DataRequired()])
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [
            (category.id, category.name)
            for category in Category.query.order_by(Category.name).all()
        ]


class CommentForm(FlaskForm):
    author = StringField('昵称', validators=[
        DataRequired(), Length(2, 30, message='昵称长度由 2 - 30 个字符组成')])
    email = StringField('邮箱', validators=[
        DataRequired(), Email(message='邮箱输入有误'),
        Length(8, 64, message='邮箱地址长度必须在 8 - 256 个字符之间')])
    site = StringField('主页', description='可选', validators=[
        Optional(), URL(message='URL 输入有误'), Length(0, 255)])
    body = TextAreaField('评论内容', validators=[
        DataRequired(), Length(2, message='评论长度最少为 2')])
    submit = SubmitField('提交')


class AdminCommentForm(CommentForm):
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()


class CategoryForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField('提交')

    def validate_name(self, filed):
        if Category.query.filter_by(name=filed.data).first():
            raise ValidationError('分类名已存在')


class LinkForm(FlaskForm):
    name = StringField('链接描述', validators=[DataRequired(), Length(1, 30)])
    url = StringField('地址', validators=[DataRequired(), URL(), Length(6, 255)])
    tag = SelectField(
        label='标签',
        validators=[DataRequired()],
        render_kw={
            'class': 'form-control'
        },
        choices=[
            ('weixin', '微信'),
            ('weibo', '微博'),
            ('douban', '豆瓣'),
            ('zhihu', '知乎'),
            ('google', '谷歌'),
            ('linkedin', '领英'),
            ('twitter', '推特'),
            ('facebook', '脸书'),
            ('github', 'Github'),
            ('telegram', 'Telegram'),
            ('other', '其它'),
            ('friendLink', '友情链接')
        ],
        default='other',
        coerce=str
    )
    submit = SubmitField('提交')


class BlogSettingForm(FlaskForm):
    blog_title = StringField('博客名称', validators=[
        DataRequired(), Length(1, 60)])
    blog_sub_title = StringField('博客副标题', validators=[
        DataRequired(), Length(1, 100)])
    name = StringField('管理员昵称', validators=[
        DataRequired(), Length(1, 30)])
    about = CKEditorField('关于', validators=[DataRequired()])
    blog_index_image = FileField('博客首页图片', validators=[
        FileAllowed(['jpg'], message='仅支持 JPG 格式')],
        description='可选，仅支持 JPG 格式图片，上传后可能需要清空浏览器缓存才能显示')
    blog_nav_image = FileField('导航栏图标', validators=[
        FileAllowed(['png'], message='仅支持 PNG 格式')],
        description='可选，仅支持 PNG 矢量图格式，上传后可能需要清空浏览器缓存才能显示')
    blog_favicon = FileField('博客favicon.ico图标', validators=[
        FileAllowed(['ico'], message='仅支持 ICO 格式')],
        description='可选, 仅支持 ICO 图标格式，上传后可能需要清空浏览器缓存才能显示')
    theme = SelectField(
        label='主题',
        render_kw={
            'class': 'form-control'
        },
        choices=[
            ('cerulean', 'Cerulean'),
            ('cosmo', 'Cosmo'),
            ('cyborg', 'Cyborg'),
            ('darkly', 'Darkly'),
            ('flatly', 'Flatly'),
            ('journal', 'Journal'),
            ('litera', 'Litera'),
            ('lumen', 'Lumen'),
            ('lux', 'Lux'),
            ('materia', 'Materia'),
            ('minty', 'Minty'),
            ('pulse', 'Pulse'),
            ('sandstone', 'Sandstone'),
            ('simplex', 'Simplex'),
            ('sketchy', 'Sketchy'),
            ('slate', 'Slate'),
            ('solar', 'Solar'),
            ('spacelab', 'Spacelab'),
            ('superhero', 'SuperHero'),
            ('united', 'United'),
            ('yeti', 'Yeti')
        ],
        default='flatly',
        coerce=str,
    )
    submit = SubmitField('提交')
