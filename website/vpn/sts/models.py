# -*- coding: utf-8 -*-
"""
    website.vpn.sts.models
    ~~~~~~~~~~~~~~~~~~~~~~

    vpn sts system models.
"""


from datetime import datetime

from website import db


class Tunnels(db.Model):
    '''tunnels models.'''
    __tablename__ = 'sts_tunnels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, index=True)
    rules = db.Column(db.String(500))
    psk = db.Column(db.String(80))
    created_at = db.Column(db.DateTime)

    def __init__(self, name, rules, psk, created_at=None):
        self.name = name
        self.rules = rules
        self.psk = psk
        if created_at is None:
            self.created_at = datetime.now()
        else:
            self.created_at = created_at

    def __repr__(self):
        return '<Tunnels %s:%s>' % (self.name, self.created_at)
