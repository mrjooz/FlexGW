# -*- coding: utf-8 -*-
"""
    website.vpn.tcp.models
    ~~~~~~~~~~~~~~~~~~~~~~~

    TCP Psystem models.
"""
from datetime import datetime

from website import db


class Connection(db.Model):

    '''TCP Proxy Connection infomation.'''
    __tablename__ = 'tcp_proxy_connection'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dest_ip = db.Column(db.String(30), nullable=False)
    dest_port = db.Column(db.Integer, nullable=False)
    local_port = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, dest_ip, dest_port, local_port, created_at=None):
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.local_port = local_port
        if created_at is None:
            self.created_at = datetime.now()
        else:
            self.created_at = created_at

    def __repr__(self):
        return '<TCP Proxy %d -> %s:%d>' % (self.local_port, self.dest_ip, self.dest_port)
