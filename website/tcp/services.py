# -*- coding: utf-8 -*-
"""
    website.tcp.services
    ~~~~~~~~~~~~~~~~

    TCP Proxy services api.
"""

import os
import sys
import subprocess
from flask import flash, current_app
from flask.ext.babel import gettext
from website.services import exec_command

from website import db
from website.tcp.models import Connection
from sqlalchemy import and_

iptables_command_prerouting = 'iptables -t nat {command} PREROUTING -p tcp --dport {local_port} -j DNAT --to-destination {dest_ip}:{dest_port};'
iptables_command_postrouting = 'iptables -t nat {command} POSTROUTING -d {dest_ip} -p tcp --dport {dest_port} -j MASQUERADE'


def get_connections():
    connections = Connection.query.all()
    return connections


def create_connection(local_port, dest_ip, dest_port):
    # 查看数据库中是否已经存在
    con = Connection.query.filter(and_(Connection.local_port == local_port, Connection.dest_ip == dest_ip, Connection.dest_port == dest_port)).first()
    if con is None:
        add_command_prerouting = iptables_command_prerouting.format(command='-A', local_port=local_port, dest_ip=dest_ip, dest_port=dest_port)
        add_command_postrouting = iptables_command_postrouting.format(command='-A', local_port=local_port, dest_ip=dest_ip, dest_port=dest_port)
        execute_command(add_command_prerouting)
        execute_command(add_command_postrouting)
        connection = Connection(dest_ip, dest_port, local_port)
        db.session.add(connection)
        db.session.commit()
        return connection


def delete_connection(connection_id):
    connection = Connection.query.get(connection_id)
    if connection is not None:
        del_command_prerouting = iptables_command_prerouting.format(command='-D', local_port=connection.local_port, dest_ip=connection.dest_ip, dest_port=connection.dest_port)
        del_command_postrouting = iptables_command_postrouting.format(command='-D', local_port=connection.local_port, dest_ip=connection.dest_ip, dest_port=connection.dest_port)
        execute_command(del_command_prerouting)
        execute_command(del_command_postrouting)
        Connection.query.filter(Connection.id == connection_id).delete()
        db.session.commit()


def execute_command(command):
    return subprocess.Popen(command.split())


def _iptables_get_dnat_rules(message=True):
    cmd = ['iptables', '-t', 'nat', '--list-rules']
    try:
        r = exec_command(cmd)
    except:
        current_app.logger.error('[SNAT]: exec_command error: %s:%s', cmd,
                                 sys.exc_info()[1])
        if message:
            flash(gettext('iptables crashed, please contact your system admin.'), 'alert')
        return False
    if r['return_code'] != 0:
        current_app.logger.error('[SNAT]: exec_command return: %s:%s:%s', cmd,
                                 r['return_code'], r['stderr'])
        if message:
            message = gettext("get rules failed: %(err)s", err=r['stderr'])
            flash(message, 'alert')
        return False
    rules = []
    for item in r['stdout'].split('\n'):
        if '-j DNAT' in item:
            t = item.split()
            if '--dport' in t and '--to-destination' in t:
                p = t[t.index('--to-destination')+1]
                address_port = p.split(':')

                if len(address_port) == 2:
                    rules.append((t[t.index('--dport')+1], address_port[0], address_port[1]))
    return rules


def ensure_iptables():
    rules_iptable = _iptables_get_dnat_rules()
    connections = Connection.query.all()
    rules_database = []
    for connection in connections:
        _connection = (str(connection.local_port), connection.dest_ip, str(connection.dest_port))
        rules_database.append(_connection)

    # 根据数据库内容调整iptables中的值
    for i in rules_database:
        if i in rules_iptable:
            rules_iptable.remove(i)
        else:
            add_command_prerouting = iptables_command_prerouting.format(command='-A', local_port=i[0], dest_ip=i[1], dest_port=i[2])
            add_command_postrouting = iptables_command_postrouting.format(command='-A', local_port=i[0], dest_ip=i[1], dest_port=i[2])
            execute_command(add_command_prerouting)
            execute_command(add_command_postrouting)

    # 去除iptables中存在但数据库中不存在的数据
    for i in rules_iptable:
        del_command_prerouting = iptables_command_prerouting.format(command='-D', local_port=i[0], dest_ip=i[1], dest_port=i[2])
        del_command_postrouting = iptables_command_postrouting.format(command='-D', local_port=i[0], dest_ip=i[1], dest_port=i[2])
        execute_command(del_command_prerouting)
        execute_command(del_command_postrouting)


def reset_iptables():
    rules_iptable = _iptables_get_dnat_rules()
    connections = Connection.query.all()
    rules_database = []
    for connection in connections:
        _connection = (str(connection.local_port), connection.dest_ip, str(connection.dest_port))
        rules_database.append(_connection)

    # 根据iptables在数据库中内容增加相应数据
    for i in rules_iptable:
        if i in rules_database:
            rules_database.remove(i)
        else:
            connection = Connection(i[1], i[2], i[0])
            db.session.add(connection)
            db.session.commit()

    # 去除数据库中多余数据
    for i in rules_database:
        Connection.query.filter_by(local_port=i[0]).filter_by(dest_ip=i[1]).filter_by(dest_port=i[2]).delete()
        db.session.commit()
