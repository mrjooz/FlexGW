# -*- coding: utf-8 -*-
"""
    website.gre.views
    ~~~~~~~~~~~~~~~~~~

    vpn views:
        /gre
        /gre/add
        /gre/del
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

from website.gre.forms import AddForm
from website.gre.forms import ConsoleForm

from website.gre.services import get_tunnels
from website.gre.services import create_tunnel
from website.gre.services import delete_tunnel
from website.gre.services import ensure_all_tunnels
from website.gre.services import reset_all_tunnels


gre = Blueprint('gre', __name__, url_prefix='/gre',
                template_folder='templates',
                static_folder='static')


@gre.route('/', methods=['GET'])
@login_required
def index():
    tunnels = get_tunnels()
    if isinstance(tunnels, list) and not tunnels:
        flash(gettext('there is not gre tunnel.'), 'info')
    return render_template('gre/index.html', tunnels=tunnels, version=__version__)


@gre.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            create_tunnel(form.local_router_ip.data, form.remote_router_ip.data, form.subnet.data)
            return redirect(url_for('gre.index'))
    return render_template('gre/add.html', form=form, version=__version__)


@gre.route('/del', methods=['POST'])
@login_required
def delete():
    delete_tunnel(request.form['tunnel_id'])
    return redirect(url_for('gre.index'))


@gre.route('/console', methods=['GET', 'POST'])
@login_required
def console():
    form = ConsoleForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.ensure.data:
                ensure_all_tunnels()
                flash(gettext('all tunnels started!'), 'success')
            if form.reset.data:
                reset_all_tunnels()
                flash(gettext('all tunnels reseted!'), 'success')
    return render_template('gre/console.html', form=form, version=__version__)
