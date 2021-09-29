# -*- coding: utf-8 -*-
"""
    website.account.views
    ~~~~~~~~~~~~~~~~~~~~~

    account views:
        /login
        /logout
"""
import cStringIO
import pyotp

from flask import Blueprint, render_template, send_file
from flask import url_for, session, redirect, request

from website import __version__
from website import db
from website.account.models import User
from website.account.models import UserDetails
from website.account.services import get_mfa_qr_code
from website.account.forms import LoginForm, MFAForm, LanguageForm

from flask.ext.login import login_required, logout_user, login_user, current_user


account = Blueprint('account', __name__,
                    template_folder='templates')


@account.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query_filter_by(username=form.account.data)
        user_details = UserDetails.query.get(user.username)
        if user_details is None:
            user_details = UserDetails(user.username, pyotp.random_base32())
            db.session.add(user_details)
            db.session.commit()

        if not user_details.otp_enabled:
            resp = redirect(request.args.get("next") or url_for('default'))
            resp.set_cookie('locale', user_details.language)
            login_user(user)

            return resp
        else:
            resp = redirect(url_for("account.mfa_verify", next=request.args.get("next")))
            resp.set_cookie('locale', user_details.language)

            session['temp_username'] = user.username
            return resp

    return render_template('account/login.html', form=form)


@account.route('/mfa/verify', methods=['GET', 'POST'])
def mfa_verify():
    form = MFAForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query_filter_by(username=session['temp_username'])
            del session['temp_username']
            login_user(user)
            return redirect(request.args.get("next") or url_for('default'))
        return redirect(url_for("account.login"))
    else:
        if 'temp_username' in session:
            return render_template('account/mfa.html', form=form)
        else:
            return redirect(url_for("account.login"))


@account.route('/logout')
@login_required
def logout():
    # Remove the user information from the session
    logout_user()
    # Remove session
    session.clear()
    return redirect(url_for("account.login"))


@account.route('/settings', methods=['GET'])
@login_required
def settings():
    form = MFAForm()
    user_details = UserDetails.query.get(current_user.username)
    language_form = LanguageForm(language=user_details.language)

    return render_template('account/settings.html', form=form, user_details=user_details, language_form=language_form, version=__version__)


@account.route('/mfa/qrcode', methods=['GET'])
@login_required
def mfa_qrcode():
    img = get_mfa_qr_code(current_user.username)
    img_buf = cStringIO.StringIO()
    img.save(img_buf)
    img_buf.seek(0)

    return send_file(img_buf, mimetype='image/png')


@account.route('/mfa/enable', methods=['POST'])
@login_required
def mfa_enable():
    form = MFAForm()
    if form.validate_on_submit():
        UserDetails.query.filter(UserDetails.username == current_user.username).update({"otp_enabled": True})
        db.session.commit()
        return redirect(url_for("account.settings"))

    user_details = UserDetails.query.get(current_user.username)
    return render_template('account/settings.html', form=form, user_details=user_details, version=__version__)


@account.route('/mfa/disable', methods=['POST'])
@login_required
def mfa_disable():
    form = MFAForm()
    if form.validate_on_submit():
        UserDetails.query.filter(UserDetails.username == current_user.username).update({"otp_enabled": False, "otp_key": pyotp.random_base32()})
        db.session.commit()
        return redirect(url_for("account.settings"))

    user_details = UserDetails.query.get(current_user.username)
    return render_template('account/settings.html', form=form, user_details=user_details, version=__version__)


@account.route('/account/language', methods=['POST'])
@login_required
def select_language():
    form = LanguageForm()
    if form.validate_on_submit():
        UserDetails.query.filter(UserDetails.username == current_user.username).update({"language": form.language.data})
        db.session.commit()
        resp = redirect(url_for("account.settings"))
        resp.set_cookie('locale', form.language.data)

        return resp

    user_details = UserDetails.query.get(current_user.username)
    return render_template('account/settings.html', form=form, user_details=user_details, version=__version__)
