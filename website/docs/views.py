# -*- coding: utf-8 -*-
"""
    website.docs.views
    ~~~~~~~~~~~~~~~~~~

    vpn views:
        /docs
"""


from flask import Blueprint, render_template
from flask.ext.login import login_required, current_user

from website.account.models import UserDetails


docs = Blueprint('docs', __name__, url_prefix='/docs',
                 template_folder='templates',
                 static_folder='static')


@docs.route('/')
@login_required
def index():
    user_details = UserDetails.query.get(current_user.username)
    return render_template('docs/%s/guide.html' % user_details.language)


@docs.route('/ipsec')
@login_required
def ipsec():
    user_details = UserDetails.query.get(current_user.username)
    return render_template('docs/%s/ipsec.html' % user_details.language)


@docs.route('/dial')
@login_required
def dial():
    user_details = UserDetails.query.get(current_user.username)
    return render_template('docs/%s/dial.html' % user_details.language)


@docs.route('/snat')
@login_required
def snat():
    user_details = UserDetails.query.get(current_user.username)
    return render_template('docs/%s/snat.html' % user_details.language)


@docs.route('/tcp')
@login_required
def tcp():
    user_details = UserDetails.query.get(current_user.username)
    return render_template('docs/%s/tcp.html' % user_details.language)


@docs.route('/certificate')
@login_required
def certificate():
    user_details = UserDetails.query.get(current_user.username)
    return render_template('docs/%s/certificate.html' % user_details.language)


@docs.route('/debug')
@login_required
def debug():
    user_details = UserDetails.query.get(current_user.username)
    return render_template('docs/%s/debug.html' % user_details.language)


@docs.route('/update')
@login_required
def update():
    user_details = UserDetails.query.get(current_user.username)
    return render_template('docs/%s/update.html' % user_details.language)


@docs.route('/changelog')
@login_required
def changelog():
    user_details = UserDetails.query.get(current_user.username)
    return render_template('docs/%s/changelog.html' % user_details.language)
