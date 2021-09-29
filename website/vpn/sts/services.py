# -*- coding: utf-8 -*-
"""
    website.vpn.sts.services
    ~~~~~~~~~~~~~~~~~~~~~~~~

    vpn site-to-site services api.
"""


import json
import sys
import time

from flask import render_template, flash, current_app
from flask.ext.babel import gettext

from website import db
from website.services import exec_command
from website.vpn.sts.models import Tunnels


class VpnConfig(object):
    ''' read and set config for vpn config file.'''
    secrets_file = '/etc/strongswan/ipsec.secrets'
    conf_file = '/etc/strongswan/ipsec.conf'

    secrets_template = 'sts/ipsec.secrets'
    conf_template = 'sts/ipsec.conf'

    _auth_types = ['secret']

    def __init__(self, conf_file=None, secrets_file=None):
        if conf_file:
            self.conf_file = conf_file
        if secrets_file:
            self.secrets_file = secrets_file

    def _get_tunnels(self):
        data = Tunnels.query.all()
        if data:
            return [{'id': item.id, 'name': item.name,
                     'psk': item.psk, 'rules': json.loads(item.rules)}
                    for item in data]
        return None

    def _commit_conf_file(self):
        tunnels = self._get_tunnels()
        data = render_template(self.conf_template, tunnels=tunnels)
        try:
            with open(self.conf_file, 'w') as f:
                f.write(data)
        except:
            current_app.logger.error('[Ipsec Services]: commit conf file error: %s:%s',
                                     self.conf_file, sys.exc_info()[1])
            return False
        return True

    def _commit_secrets_file(self):
        data = self._get_tunnels()
        if data:
            tunnels = [{'leftid': i['rules']['leftid'],
                        'rightid': i['rules']['rightid'],
                        'psk': i['psk']} for i in data]
        else:
            tunnels = None
        data = render_template(self.secrets_template, tunnels=tunnels)
        try:
            with open(self.secrets_file, 'w') as f:
                f.write(data)
        except:
            current_app.logger.error('[Ipsec Services]: commit secrets file error: %s:%s',
                                     self.secrets_file, sys.exc_info()[1])
            return False
        return True

    def update_tunnel(self, tunnel_id, tunnel_name, rules, psk):
        #: store to instance
        self.tunnel = Tunnels.query.filter_by(id=tunnel_id).first()
        if self.tunnel is None:
            self.tunnel = Tunnels(tunnel_name, rules, psk)
            db.session.add(self.tunnel)
        else:
            self.tunnel.name = tunnel_name
            self.tunnel.rules = rules
            self.tunnel.psk = psk
        db.session.commit()
        return True

    def delete(self, id):
        tunnel = Tunnels.query.filter_by(id=id).first()
        db.session.delete(tunnel)
        db.session.commit()
        return True

    def commit(self):
        if self._commit_conf_file() and self._commit_secrets_file():
            return True
        return False


class VpnServer(object):
    """vpn server console"""
    def __init__(self):
        self.cmd = None
        self.c_code = None
        self.c_stdout = None
        self.c_stderr = None

    def __repr__(self):
        return '<VpnServer %s:%s:%s:%s>' % (self.cmd, self.c_code,
                                            self.c_stdout, self.c_stderr)

    def _exec(self, cmd, message=None):
        try:
            r = exec_command(cmd)
        except:
            current_app.logger.error('[Ipsec Services]: exec_command error: %s:%s',
                                     cmd, sys.exc_info()[1])
            flash(gettext('Strongswan crashed, please contact your system administrator!'), 'alert')
            return False
        #: store cmd info
        self.cmd = cmd
        self.c_code = r['return_code']
        self.c_stdout = [i for i in r['stdout'].split('\n') if i]
        self.c_stderr = [i for i in r['stderr'].split('\n') if i]
        #: check return code
        if r['return_code'] == 0:
            return True
        if message:
            flash(message + r['stderr'], 'alert')
        current_app.logger.error('[Ipsec Services]: exec_command return: %s:%s:%s',
                                 cmd, r['return_code'], r['stderr'])
        return False

    def _tunnel_exec(self, cmd, message=None):
        if not self._exec(cmd, message):
            return False
        #: check return data
        try:
            r = self.c_stdout[-1]
        except IndexError:
            current_app.logger.error('[Ipsec Services]: exec_command return: %s:%s:%s:%s',
                                     cmd, self.c_code, self.c_stdout, self.c_stderr)
            flash(gettext('command has been executed but no data retrived.'), 'alert')
            return False
        #: check return status
        if self.c_code == 0 and "failed" not in r:
            return True
        else:
            current_app.logger.error('[Ipsec Services]: exec_command return: %s:%s:%s:%s',
                                     cmd, self.c_code, self.c_stdout, self.c_stderr)
            flash(message + " ".join(self.c_stderr), 'alert')
            return False

    def _reload_conf(self):
        cmd = ['strongswan', 'reload']
        message = gettext('vpn config file reload failed!')
        return self._exec(cmd, message)

    def _rereadsecrets(self):
        cmd = ['strongswan', 'rereadsecrets']
        message = gettext('vpn secret file reload failed!')
        return self._exec(cmd, message)

    @property
    def start(self):
        if self.status:
            flash(gettext('strongswan already started!'), 'info')
            return False
        cmd = ['strongswan', 'start']
        message = gettext('strongswan start failed!')
        return self._exec(cmd, message)

    @property
    def stop(self):
        if not self.status:
            flash(gettext('strongswan already stopped!'), 'info')
            return False
        cmd = ['strongswan', 'stop']
        message = gettext('strongswan stop failed!')
        return self._exec(cmd, message)

    @property
    def reload(self):
        tunnel = VpnConfig()
        if not tunnel.commit():
            message = gettext('vpn config files reload failed, please retry!')
            flash(message, 'alert')
            return False
        if not self.status:
            flash(gettext('vpn config files reload successed, but strongswan is not running.'), 'alert')
            return False
        if self._reload_conf() and self._rereadsecrets():
            return True
        return False

    @property
    def status(self):
        cmd = ['strongswan', 'status']
        return self._exec(cmd)

    def tunnel_status(self, tunnel_name):
        cmd = ['strongswan', 'status', tunnel_name]
        if self._exec(cmd):
            for item in self.c_stdout:
                if 'INSTALLED' in item:
                    return True
        return False

    def tunnel_up(self, tunnel_name):
        if self.tunnel_status(tunnel_name):
            flash(gettext('tunnel already up.'), 'info')
            return False
        cmd = ['strongswan', 'up', tunnel_name]
        message = gettext('tunnel start failed:')
        return self._tunnel_exec(cmd, message)

    def tunnel_down(self, tunnel_name):
        if not self.tunnel_status(tunnel_name):
            flash(gettext('tunnel already down.'), 'info')
            return False
        cmd = ['strongswan', 'down', tunnel_name]
        message = gettext('tunnel stop failed:')
        return self._tunnel_exec(cmd, message)

    def tunnel_traffic(self, tunnel_name):
        cmd = ['strongswan', 'statusall', tunnel_name]
        rx_pkts = 0
        tx_pkts = 0
        raw_data = None
        if self._exec(cmd):
            for line in self.c_stdout:
                if 'bytes_i' in line:
                    raw_data = line.replace(',', '').split()
            if not raw_data:
                return False
            if raw_data[raw_data.index('bytes_i')+1].startswith('('):
                #: check Timestamp > 2s, then drop.
                if int(raw_data[raw_data.index('bytes_i')+3].strip('s')) < 2:
                    tx_pkts = raw_data[raw_data.index('bytes_i')+1].strip('(')
            if raw_data[raw_data.index('bytes_o')+1].startswith('('):
                #: check Timestamp > 2s, then drop.
                if int(raw_data[raw_data.index('bytes_o')+3].strip('s')) < 2:
                    rx_pkts = raw_data[raw_data.index('bytes_o')+1].strip('(')
            return {'rx_pkts': int(rx_pkts),
                    'tx_pkts': int(tx_pkts),
                    'time': int(time.time())}
        return False


def vpn_settings(form, tunnel_id=None):
    tunnel = VpnConfig()
    vpn = VpnServer()
    local_subnet = ','.join([i.strip() for i in form.local_subnet.data.split(',')])
    remote_subnet = ','.join([i.strip() for i in form.remote_subnet.data.split(',')])
    if form.esp_dh_algorithm.data == 'null':
        esp = '%s-%s' % (form.esp_encryption_algorithm.data, form.esp_integrity_algorithm.data)
    else:
        esp = '%s-%s-%s' % (form.esp_encryption_algorithm.data, form.esp_integrity_algorithm.data, form.esp_dh_algorithm.data)
    ike = '%s-%s-%s' % (form.ike_encryption_algorithm.data, form.ike_integrity_algorithm.data, form.ike_dh_algorithm.data)
    rules = {'left': '0.0.0.0', 'leftsubnet': local_subnet,
             'leftid': form.local_id.data, 'right': form.remote_ip.data,
             'rightsubnet': remote_subnet, 'rightid': form.remote_id.data,
             'authby': 'secret', 'esp': esp,
             'ike': ike, 'auto': form.start_type.data,
             'aggressive': form.negotiation_mode.data, 'dpdaction': form.dpd_action.data,
             'keyexchange': form.keyexchange.data}
    if tunnel.update_tunnel(tunnel_id, form.tunnel_name.data, json.dumps(rules),
                            form.psk.data) and vpn.reload:
        return True
    return False


def vpn_del(id):
    config = VpnConfig()
    vpn = VpnServer()
    tunnel = get_tunnels(id, True)[0]
    if tunnel['status']:
        vpn.tunnel_down(tunnel['name'])
    if config.delete(id) and vpn.reload:
        return True
    return False


def get_tunnels(id=None, status=False):
    if id:
        data = Tunnels.query.filter_by(id=id)
    else:
        data = Tunnels.query.all()
    if data:
        tunnels = [{'id': item.id, 'name': item.name, 'psk': item.psk,
                    'rules': json.loads(item.rules)} for item in data]
        if status:
            vpn = VpnServer()
            for tunnel in tunnels:
                tunnel['status'] = vpn.tunnel_status(tunnel['name'])
        return sorted(tunnels, key=lambda x: x.get('status'), reverse=True)
    return None
