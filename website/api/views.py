# -*- coding: utf-8 -*-
"""
    website.api.views
    ~~~~~~~~~~~~~~~~~

    vpn api views:
        /api/*
"""


import sys
import json
import requests

from flask import Blueprint, jsonify, current_app

from flask.ext.login import login_required

from website.services import exec_command
from website.utils import ad
from website.vpn.sts.services import VpnServer


api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/vpn/<tunnel_name>/traffic/now')
@login_required
def vpn_traffic(tunnel_name):
    vpn = VpnServer()
    return jsonify(vpn.tunnel_traffic(tunnel_name) or [])


@api.route('/vpn/<tunnel_name>/up')
@login_required
def tunnel_up(tunnel_name):
    vpn = VpnServer()
    return jsonify({'result': vpn.tunnel_up(tunnel_name), 'stdout': vpn.c_stdout})


@api.route('/checkupdate')
def check_update():
    cmd = ['/usr/local/flexgw/scripts/update', '--check']
    try:
        r = exec_command(cmd, timeout=10)
    except:
        current_app.logger.error('[API]: exec_command error: %s:%s', cmd,
                                 sys.exc_info()[1])
        return jsonify({"message": u"执行命令：`/usr/local/flexgw/scripts/update --check' 失败!"}), 500
    if r['return_code'] != 0:
        current_app.logger.error('[API]: exec_command return: %s:%s:%s', cmd,
                                 r['return_code'], r['stderr'])
        return jsonify({"message": u"检查更新失败，请手工执行命令：`/usr/local/flexgw/scripts/update --check'"}), 504
    for line in r['stdout'].split('\n'):
        if ' new ' in line:
            info = u"发现新版本：%s！" % (line.split(':')[1])
            return jsonify({"message": info})
    return jsonify({"message": u"已经是最新版本了！"}), 404


@api.route("/ad/<ad_type>")
def get_ads(ad_type):
    ad_id = None
    if ad_type == 'top':
        ad_id = "AD1121"
    elif ad_type == 'bottom':
        ad_id = "AD1122"
    ads = []
    if ad_id is not None:
        # url = ad.ad_url(ad_id, current_app.debug)
        url = ad.ad_url(ad_id, False)
        resp = requests.get(url)
        if resp.status_code == 200:
            ads = ad.convert_ads(json.loads(resp.text))
    return jsonify({"ads": ads})
