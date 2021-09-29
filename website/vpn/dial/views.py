# -*- coding: utf-8 -*-
"""
    website.vpn.dial.views
    ~~~~~~~~~~~~~~~~~~~~~~

    vpn dial views:
        /vpn/dial/settings
        /vpn/dial/add
        /vpn/dial/<int:id>
        /vpn/dial/<int:id>/settings
"""

from flask import Blueprint, render_template
from flask import url_for, redirect
from flask import flash

from flask.ext.login import login_required
from flask.ext.babel import gettext

from website import __version__
from website.vpn.dial.services import get_accounts, account_update, account_del
from website.vpn.dial.services import VpnServer, settings_update
from website.vpn.dial.forms import AddForm, SettingsForm, ConsoleForm
from website.vpn.dial.models import Account, Settings


dial = Blueprint('dial', __name__, url_prefix='/vpn/dial',
                 template_folder='templates',
                 static_folder='static')


@dial.route('/')
@login_required
def index():
    accounts = get_accounts(status=True)
    if not accounts:
        flash(gettext('there is no vpn config yet.'), 'info')
    return render_template('dial/index.html', accounts=accounts, version=__version__)


@dial.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    settings = Settings.query.get(1)
    if not settings:
        flash(gettext('please config vpn before add account.'), 'alert')
        return redirect(url_for('dial.settings'))
    form = AddForm()
    if form.validate_on_submit():
        if not Account.query.filter_by(name=form.name.data).first():
            if account_update(form):
                message = gettext('add vpn account successed.')
                flash(message, 'success')
                return redirect(url_for('dial.index'))
        else:
            message = gettext('the account is exist: %(account)s', account=form.name.data)
            flash(message, 'alert')
    return render_template('dial/add.html', form=form, version=__version__)


@dial.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    settings = Settings.query.get(1)
    if form.validate_on_submit():
        if settings_update(form):
            flash(gettext('vpn config update successed!'), 'success')
            return redirect(url_for('dial.settings'))
    if settings:
        form.subnet.data = settings.subnet
        form.c2c.data = 'yes' if settings.c2c else 'no'
        form.duplicate.data = 'yes' if settings.duplicate else 'no'
        form.proto.data = settings.proto
    return render_template('dial/settings.html', settings=settings, form=form, version=__version__)


@dial.route('/<int:id>/settings', methods=['GET', 'POST'])
@login_required
def id_settings(id):
    form = AddForm()
    account = get_accounts(id)
    if form.validate_on_submit():
        if form.delete.data:
            if account_del(id):
                message = gettext('account deleted: %(account)s', account=account[0]['name'])
                flash(message, 'success')
                return redirect(url_for('dial.index'))
        if form.save.data:
            if account_update(form, id):
                flash(gettext('update account successed'), 'success')
                return redirect(url_for('dial.id_settings', id=id))
    return render_template('dial/view.html', account=account[0], form=form, version=__version__)


@dial.route('/console', methods=['GET', 'POST'])
@login_required
def console():
    form = ConsoleForm()
    vpn = VpnServer()
    if form.validate_on_submit():
        if form.stop.data and vpn.stop:
            flash(gettext('vpn service stopped!'), 'success')
        if form.start.data and vpn.start:
            flash(gettext('vpn service started!'), 'success')
        if form.re_load.data and vpn.reload:
            flash(gettext('vpn service reloaded!'), 'success')
        return redirect(url_for('dial.console'))
    return render_template('dial/console.html', status=vpn.status, form=form, version=__version__)


@dial.route('/download')
@login_required
def download():
    return render_template('dial/download.html', version=__version__)
