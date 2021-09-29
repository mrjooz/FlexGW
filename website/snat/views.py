# -*- coding: utf-8 -*-
"""
    website.snat.views
    ~~~~~~~~~~~~~~~~~~

    vpn views:
        /snat
"""


from flask import Blueprint, render_template
from flask import url_for, redirect, flash
from flask import request

from flask.ext.login import login_required
from flask.ext.babel import gettext

from website import __version__
from website.snat.forms import ConsoleForm

from website.snat.forms import SnatForm
from website.snat.services import iptables_get_snat_rules, iptables_set_snat_rules
from website.snat.services import ensure_iptables, reset_iptables

snat = Blueprint('snat', __name__, url_prefix='/snat',
                 template_folder='templates',
                 static_folder='static')


@snat.route('/')
@login_required
def index():
    rules = iptables_get_snat_rules()
    if isinstance(rules, list) and not rules:
        flash(gettext('there is no snat ruls yet.'), 'info')
    return render_template('index.html', rules=rules, version=__version__)


@snat.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = SnatForm()
    if form.validate_on_submit():
        if iptables_set_snat_rules('add', form.source.data, form.gateway.data):
            message = gettext("snat rule is added: %(source)s ==> %(gateway)s.", source=form.source.data, gateway=form.gateway.data)
            flash(message, 'success')
            return redirect(url_for('snat.index'))
    return render_template('add.html', form=form, version=__version__)


@snat.route('/del', methods=['POST'])
@login_required
def delete():
    source = request.form['source']
    gateway = request.form['gateway']
    if iptables_set_snat_rules('del', source, gateway):
        message = gettext("snat rule is gettextd: %(source)s ==> %(gateway)s.", source=source, gateway=gateway)
        flash(message, 'success')
    return redirect(url_for('snat.index'))


@snat.route('/console', methods=['GET', 'POST'])
@login_required
def console():
    form = ConsoleForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.ensure.data:
                ensure_iptables()
                flash(gettext('all snat started!'), 'success')
            if form.reset.data:
                reset_iptables()
                flash(gettext('all snat reseted!'), 'success')
    return render_template('console.html', form=form, version=__version__)
