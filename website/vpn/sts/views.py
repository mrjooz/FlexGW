# -*- coding: utf-8 -*-
"""
    website.vpn.sts.views
    ~~~~~~~~~~~~~~~~~~~~~

    vpn sts views:
        /vpn/sts/add
        /vpn/sts/<int:id>
        /vpn/sts/<int:id>/settings
"""

from flask import Blueprint, render_template
from flask import url_for, redirect
from flask import flash

from website import __version__
from website.vpn.sts.forms import AddForm
from website.vpn.sts.forms import ConsoleForm, UpDownForm
from website.vpn.sts.services import vpn_settings, vpn_del
from website.vpn.sts.services import get_tunnels, VpnServer
from website.vpn.sts.models import Tunnels

from flask.ext.login import login_required
from flask.ext.babel import gettext


sts = Blueprint('sts', __name__, url_prefix='/vpn/sts',
                template_folder='templates')


@sts.route('/')
@login_required
def index():
    form = UpDownForm()
    tunnels = get_tunnels(status=True)
    if not tunnels:
        flash(gettext('there is no vpn config yet.'), 'info')
    return render_template('sts/index.html', version=__version__, tunnels=tunnels, form=form)


@sts.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddForm()
    if form.validate_on_submit():
        if not Tunnels.query.filter_by(name=form.tunnel_name.data).first():
            if vpn_settings(form):
                message = gettext('site to site tunnel has been added!')
                flash(message, 'success')
                return redirect(url_for('sts.index'))
        else:
            message = gettext('tunnel exist: %(tunnel_name)s', tunnel_name=form.tunnel_name.data)
            flash(message, 'alert')
    return render_template('sts/add.html', version=__version__, form=form)


@sts.route('/<int:id>/settings', methods=['GET', 'POST'])
@login_required
def settings(id):
    form = AddForm()
    tunnel = get_tunnels(id)
    if form.validate_on_submit():
        if form.delete.data:
            if vpn_del(id):
                message = gettext('tunnel %(tunnel_name)s has been deleted!', tunnel_name=tunnel[0]['name'])
                flash(message, 'success')
                return redirect(url_for('sts.index'))
        if form.save.data:
            if vpn_settings(form, id):
                flash(gettext('tunnel config has been updated!'), 'success')
                return redirect(url_for('sts.settings', id=id))
    form.keyexchange.data = tunnel[0]['rules']['keyexchange']
    form.local_subnet.data = tunnel[0]['rules']['leftsubnet']
    form.remote_subnet.data = tunnel[0]['rules']['rightsubnet']
    form.start_type.data = tunnel[0]['rules']['auto']
    form.negotiation_mode.data = tunnel[0]['rules']['aggressive']
    form.dpd_action.data = tunnel[0]['rules']['dpdaction']
    form.local_id.data = tunnel[0]['rules']['leftid']
    form.remote_id.data = tunnel[0]['rules']['rightid']
    # Backward compatible v1.1.0
    esp_settings = tunnel[0]['rules']['esp'].split('-')
    form.esp_encryption_algorithm.data = esp_settings[0]
    form.esp_integrity_algorithm.data = esp_settings[1]
    form.esp_dh_algorithm.data = esp_settings[2] if len(esp_settings) == 3 else 'null'
    ike_settings = tunnel[0]['rules'].get('ike', 'aes128-sha1-modp2048').split('-')
    form.ike_encryption_algorithm.data = ike_settings[0]
    form.ike_integrity_algorithm.data = ike_settings[1]
    form.ike_dh_algorithm.data = ike_settings[2]
    return render_template('sts/view.html', version=__version__, tunnel=tunnel[0], form=form)


@sts.route('/<int:id>/flow')
@login_required
def flow(id):
    tunnel = get_tunnels(id, status=True)
    return render_template('sts/flow.html', version=__version__, tunnel=tunnel[0])


@sts.route('/console', methods=['GET', 'POST'])
@login_required
def console():
    form = ConsoleForm()
    vpn = VpnServer()
    if form.validate_on_submit():
        if form.stop.data and vpn.stop:
            flash(gettext('strongswan has been stopped!'), 'success')
        if form.start.data and vpn.start:
            flash(gettext('strongswan has been started!'), 'success')
        if form.re_load.data and vpn.reload:
            flash(gettext('strongswan has been reloaded!'), 'success')
    return render_template('sts/console.html', version=__version__, status=vpn.status, form=form)


@sts.route('/updown', methods=['POST'])
@login_required
def updown():
    form = UpDownForm()
    vpn = VpnServer()
    if form.validate_on_submit():
        if form.up.data and vpn.tunnel_up(form.tunnel_name.data):
            flash(gettext('tunnel is up!'), 'success')
        if form.down.data and vpn.tunnel_down(form.tunnel_name.data):
            flash(gettext('tunnel is down!'), 'success')
    return redirect(url_for('sts.index'))
