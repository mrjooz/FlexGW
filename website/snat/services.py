# -*- coding: utf-8 -*-
"""
    website.snat.services
    ~~~~~~~~~~~~~~~~~~~~~

    snat services api.
"""


import sys

from flask import flash, current_app

from flask.ext.babel import gettext

from website.services import exec_command
from website.snat.models import SNAT
from website import db


def iptables_get_snat_rules(message=True):
    snat = SNAT.query.all()
    rules_iptable = []
    for snat_item in snat:
        source = snat_item.source
        gateway = snat_item.gateway
        _snat_item = (source, gateway)
        rules_iptable.append(_snat_item)

    return rules_iptable


def _iptables_get_snat_rules(message=True):
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
        if '-j SNAT' in item:
            t = item.split()
            if '-s' in t:
                rules.append((t[t.index('-s')+1], t[t.index('--to-source')+1]))
    return rules


def iptables_set_snat_rules(method, source, gateway, message=True):
    if method == 'add':
        if _iptables_set_snat_rules(method, source, gateway, message):
            snat = SNAT(source, gateway)
            try:
                # add data into database
                db.session.add(snat)
                db.session.commit()
            except Exception as ex:
                _iptables_set_snat_rules('del', source, gateway)
                current_app.logger.error('[SNAT]: db commit error: %s', ex)
                return False
            return True

    elif method == 'del':
        if _iptables_set_snat_rules(method, source, gateway, message):
            snat = SNAT(source, gateway)
            try:
                # add data into database
                SNAT.query.filter_by(source=source).filter_by(gateway=gateway).delete()
                db.session.commit()
            except Exception as ex:
                _iptables_set_snat_rules('del', source, gateway)
                current_app.logger.error('[SNAT]: db commit error: %s', ex)
                return False
            return True
    return False


def _iptables_set_snat_rules(method, source, gateway, message=True):
    methods = {'add': '-A', 'del': '-D'}
    #: check rule exist while add rule
    rules = _iptables_get_snat_rules()
    if isinstance(rules, bool) and not rules:
        return False
    if method == 'add' and (source, gateway) in rules:
        if message:
            message = gettext("the rule already exist: %(source)s ==> %(gateway)s", source=source, gateway=gateway)
            flash(message, 'alert')
        return False
    #: add rule to iptables
    cmd = 'iptables -t nat %s POSTROUTING -s %s -j SNAT --to-source %s' % (methods[method], source, gateway)
    save_rules = 'iptables-save -t nat'
    try:
        with open('/usr/local/flexgw/instance/snat-rules.iptables', 'w') as f:
            results = exec_command(cmd.split()), exec_command(save_rules.split(), stdout=f)
    except:
        current_app.logger.error('[SNAT]: exec_command error: %s:%s', cmd,
                                 sys.exc_info()[1])
        if message:
            flash(gettext('iptables crashed, please contact your system admin.'), 'alert')
        return False

    #: check result
    for r, c in zip(results, [cmd, save_rules]):
        if r['return_code'] == 0:
            continue
        elif message:
            message = gettext("set rule failed: %(err)s", err=r['stderr'])
            flash(message, 'alert')
        current_app.logger.error('[SNAT]: exec_command return: %s:%s:%s', c,
                                 r['return_code'], r['stderr'])
        return False

    return True


def ensure_iptables():
    rules_iptable = _iptables_get_snat_rules()
    snat = SNAT.query.all()
    rules_database = []
    for snat_item in snat:
        _snat_item = (snat_item.source, snat_item.gateway)
        rules_database.append(_snat_item)

    # 根据数据库内容调整iptables中的值
    for i in rules_database:
        if i in rules_iptable:
            rules_iptable.remove(i)
        else:
            _iptables_set_snat_rules('add', i[0], i[1])

    # 去除iptables中存在但数据库中不存在的数据
    for i in rules_iptable:
        _iptables_set_snat_rules('del', i[0], i[1])


def reset_iptables():
    rules_iptable = _iptables_get_snat_rules()
    snat = SNAT.query.all()
    rules_database = []
    for snat_item in snat:
        _snat_item = (snat_item.source, snat_item.gateway)
        rules_database.append(_snat_item)

    # 根据iptables在数据库中内容增加相应数据
    for i in rules_iptable:
        if i in rules_database:
            rules_database.remove(i)
        else:
            snat = SNAT(i[0], i[1])
            db.session.add(snat)
            db.session.commit()

    # 去除数据库中多余数据
    for i in rules_database:
        SNAT.query.filter_by(source=i[0]).filter_by(gateway=i[1]).delete()
        db.session.commit()
