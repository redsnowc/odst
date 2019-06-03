# -*- coding: utf-8 -*-
"""
    :author: 秋荏苒
    :copyright: © 2019 by 秋荏苒 <nuanyang.44@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
import os
import sys
from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for, current_app

from app.configs import basedir


def is_safe_url(target):
    """
    Make sure the redirect URLs safely
    :param target: url address
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in (
        'http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='web.index', **kwargs):
    """
    If next is not none, redirect next, if not, redirect index page
    """
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in \
           current_app.config['BLOG_ALLOWED_IMAGE_EXTENSIONS']


def upload_file(file, prefix):
    """
    For save file with what prefix you like
    """
    file.filename = prefix + '.' + file.filename.rsplit('.', 1)[1]
    if sys.platform.startswith('win'):
        upload_path = os.path.join(basedir, r'app\static\images')
    else:
        upload_path = os.path.join(basedir, 'app/static/images')
    file.save(os.path.join(upload_path, file.filename))
