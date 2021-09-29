# -*- coding: utf-8 -*-
"""
    website.vpn.tcp.models
    ~~~~~~~~~~~~~~~~~~~~~~~

    TCP Psystem models.
"""
from datetime import datetime

from website import db


class GRETunnel(db.Model):

    '''GRE tunnel infomation.'''
    __tablename__ = 'gre_tunnel'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    local_router_ip = db.Column(db.String(30), nullable=False)
    remote_router_ip = db.Column(db.String(30), nullable=False)
    subnet = db.Column(db.Integer, nullable=False)
    tunnel_id = db.Column(db.Integer, unique=True)
    ttl = db.Column(db.Integer, nullable=False, default=255)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, local_router_ip, remote_router_ip, subnet, tunnel_id, ttl=255, created_at=None):
        self.local_router_ip = local_router_ip
        self.remote_router_ip = remote_router_ip
        self.subnet = subnet
        self.tunnel_id = tunnel_id
        self.ttl = ttl
        if created_at is None:
            self.created_at = datetime.now()
        else:
            self.created_at = created_at

    def __repr__(self):
        return '<GRE Tunnel %s -> %s>' % (self.local_router_ip, self.remote_router_ip)
