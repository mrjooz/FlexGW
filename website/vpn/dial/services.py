# -*- coding: utf-8 -*-
"""
    website.vpn.dial.services
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    vpn dial services api.
"""


import copy
import os
import sys
from datetime import datetime

from flask import render_template, flash, current_app
from flask.ext.babel import gettext

from website import db
from website.services import exec_command
from website.vpn.dial.models import Account, Settings
from website.vpn.dial.helpers import exchange_maskint


class VpnConfig(object):

    ''' read and set config for vpn config file.'''
    conf_file = '/etc/openvpn/server/server.conf'
    client_conf_file = '/usr/local/flexgw/rc/openvpn-client.conf'

    conf_template = 'dial/server.conf'
    client_conf_template = 'dial/client.conf'

    def __init__(self, conf_file=None):
        if conf_file:
            self.conf_file = conf_file

    def _get_settings(self):
        data = Settings.query.get(1)
        if data:
            return data
        return None

    def _commit_conf_file(self):
        r_data = self._get_settings()
        r_ipool = r_data.ipool
        r_subnet = r_data.subnet
        proto = r_data.proto
        c2c = r_data.c2c
        duplicate = r_data.duplicate
        ipool = "%s %s" % (r_ipool.split('/')[0].strip(),
                           exchange_maskint(int(r_ipool.split('/')[1].strip())))
        subnets = ["%s %s" % (i.split('/')[0].strip(),
                              exchange_maskint(int(i.split('/')[1].strip())))
                   for i in r_subnet.split(',')]
        server_data = render_template(self.conf_template, ipool=ipool, subnets=subnets,
                                      c2c=c2c, duplicate=duplicate, proto=proto)
        client_data = render_template(self.client_conf_template, proto=proto)
        try:
            with open(self.conf_file, 'w') as f:
                f.write(server_data)
            with open(self.client_conf_file, 'w') as f:
                f.write(client_data)
        except:
            current_app.logger.error('[Dial Services]: commit conf file error: %s',
                                     sys.exc_info()[1])
            return False
        return True

    def update_account(self, id, name, password):
        account = Account.query.filter_by(id=id).first()
        if account is None:
            account = Account(name, password)
            db.session.add(account)
        else:
            account.name = name
            account.password = password
        db.session.commit()
        return True

    def update_settings(self, ipool, subnet, c2c, duplicate, proto):
        choice = {"yes": True, "no": False}
        proto_type = {"tcp": "tcp", "udp": "udp"}
        subnet_list = [i.strip() for i in subnet.split(',')]
        subnet = ','.join(subnet_list)
        settings = Settings.query.get(1)
        if settings is None:
            settings = Settings(ipool, subnet, choice[c2c], choice[duplicate],
                                proto_type.get(proto, 'udp'))
            db.session.add(settings)
        else:
            settings.ipool = ipool
            settings.subnet = subnet
            settings.c2c = choice[c2c]
            settings.duplicate = choice[duplicate]
            settings.proto = proto_type.get(proto, 'udp')
        db.session.commit()
        return True

    def delete(self, id):
        account = Account.query.filter_by(id=id).first()
        db.session.delete(account)
        db.session.commit()
        return True

    def commit(self):
        if self._commit_conf_file():
            return True
        return False


class VpnServer(object):

    """vpn server console"""
    log_file = '/etc/openvpn/server/openvpn-status.log'
    pid_file = '/var/run/openvpn-server/server.pid'

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
            current_app.logger.error('[Dial Services]: exec_command error: %s:%s', cmd,
                                     sys.exc_info()[1])
            flash(gettext("OpenVPN is crashed, please contact your system admin."), 'alert')
            return False
        #: store cmd info
        self.cmd = cmd
        self.c_code = r['return_code']
        self.c_stdout = r['stdout']
        self.c_stderr = r['stderr']
        #: check return code
        if r['return_code'] == 0:
            return True
        if message:
            flash(message + r['stderr'], 'alert')
        current_app.logger.error('[Dial Services]: exec_command return: %s:%s:%s', cmd,
                                 r['return_code'], r['stderr'])
        return False

    def _reload_conf(self):
        cmd = ['systemctl', 'restart', 'openvpn-server@server']
        message = gettext('vpn service reload failed!')
        return self._exec(cmd, message)

    def _package_client_conf(self):
        cmd = ['/usr/local/flexgw/scripts/packconfig', 'all']
        message = gettext('client config packaging failed!')
        return self._exec(cmd, message)

    @property
    def start(self):
        if self.status:
            flash(gettext('service already started!'), 'info')
            return False
        cmd = ['systemctl', 'start', 'openvpn-server@server']
        message = gettext('vpn service start failed!')
        return self._exec(cmd, message)

    @property
    def stop(self):
        if not self.status:
            flash(gettext('service already stopped.'), 'info')
            return False
        cmd = ['systemctl', 'stop', 'openvpn-server@server']
        message = gettext('vpn service stop failed')
        return self._exec(cmd, message)

    @property
    def reload(self):
        tunnel = VpnConfig()
        if not tunnel.commit():
            message = gettext('vpn config file set failed, please retry!')
            flash(message, 'alert')
            return False
        self._package_client_conf()
        if not self.status:
            flash(gettext('vpn config file set successed, vpn service is not running.'), 'alert')
            return False
        if self._reload_conf():
            return True
        return False

    @property
    def status(self):
        if not os.path.isfile(self.pid_file):
            return False

        try:
            with open(self.pid_file) as f:
                raw_data = f.readlines()
        except:
            current_app.logger.error('[Dial Services]: open pid file error: %s:%s',
                                     self.pid_file, sys.exc_info()[1])
            return False
        if not raw_data:
            return False
        pid = int(raw_data[0])
        cmd = ['kill', '-0', str(pid)]
        return self._exec(cmd)

    def account_status(self, account_name):
        result = []
        if not self.status:
            return False
        try:
            with open(self.log_file) as f:
                raw_data = f.readlines()
        except:
            current_app.logger.error('[Dial Services]: open status log file error: %s:%s',
                                     self.log_file, sys.exc_info()[1])
            return False
        for line in raw_data:
            if line.startswith('CLIENT_LIST,%s,' % account_name):
                data = line.split(',')
                result.append({'rip': '%s' % data[2], 'vip': '%s' % data[3],
                               'br': data[4], 'bs': data[5], 'ct': data[7]})
        return result or False

    def tunnel_traffic(self, tunnel_name):
        pass


def get_accounts(id=None, status=False):
    result = []
    if id:
        data = Account.query.filter_by(id=id)
    else:
        data = Account.query.all()

    if data:
        accounts = [{'id': i.id, 'name': i.name,
                     'password': i.password, 'created_at': i.created_at.strftime('%Y-%m-%d %H:%M:%S')}
                    for i in data]
        if status:
            vpn = VpnServer()
            for account in accounts:
                statuses = vpn.account_status(account['name'])
                if statuses:
                    for status in statuses:
                        account['rip'] = status['rip'].split(':')[0]
                        account['vip'] = status['vip']
                        account['br'] = status['br']
                        account['bs'] = status['bs']
                        account['ct'] = datetime.strptime(status['ct'],'%a %b %d %H:%M:%S %Y')
                        result.append(copy.deepcopy(account))
                else:
                    result.append(copy.deepcopy(account))
        return sorted(result or accounts, key=lambda x: x.get('rip'), reverse=True)
    return None


def account_update(form, id=None):
    account = VpnConfig()
    if account.update_account(id, form.name.data, form.password.data):
        return True
    return False


def account_del(id):
    config = VpnConfig()
    vpn = VpnServer()
    if config.delete(id) and vpn.reload:
        return True
    return False


def settings_update(form):
    account = VpnConfig()
    vpn = VpnServer()
    if account.update_settings(form.ipool.data,
                               form.subnet.data,
                               form.c2c.data,
                               form.duplicate.data,
                               form.proto.data) and vpn.reload:
        return True
    return False
