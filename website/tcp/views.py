# -*- coding: utf-8 -*-
"""
    website.tcp.views
    ~~~~~~~~~~~~~~~~~~

    vpn views:
        /tcp
        /tcp/add
        /tcp/del
"""


from flask import Blueprint
from flask import render_template
from flask import url_for
from flask import redirect
from flask import flash
from flask import request

from flask.ext.login import login_required
from flask.ext.babel import gettext

from website import __version__

from website.tcp.forms import AddForm
from website.tcp.forms import ConsoleForm

from website.tcp.services import get_connections
from website.tcp.services import create_connection
from website.tcp.services import delete_connection
from website.tcp.services import reset_iptables, ensure_iptables


tcp = Blueprint('tcp', __name__, url_prefix='/tcp',
                template_folder='templates',
                static_folder='static')


@tcp.route('/', methods=['GET'])
@login_required
def index():
    connections = get_connections()
    if isinstance(connections, list) and not connections:
        flash(gettext('there is no tcp tunnel yet.'), 'info')
    return render_template('tcp/index.html', connections=connections, version=__version__)


@tcp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            create_connection(form.local_port.data, form.dest_ip.data, form.dest_port.data)
            return redirect(url_for('tcp.index'))
    return render_template('tcp/add.html', form=form, version=__version__)


@tcp.route('/del', methods=['POST'])
@login_required
def delete():
    delete_connection(request.form['connection_id'])
    return redirect(url_for('tcp.index'))


@tcp.route('/console', methods=['GET', 'POST'])
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
    return render_template('tcp/console.html', form=form, version=__version__)
