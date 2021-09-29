# -*- coding: utf-8 -*-
"""
    website.vpn.dial.models
    ~~~~~~~~~~~~~~~~~~~~~~~

    vpn dial system models.
"""


from datetime import datetime

from website import db


class Account(db.Model):
    '''dial name.'''
    __tablename__ = 'dial_account'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, index=True)
    password = db.Column(db.String(80))
    created_at = db.Column(db.DateTime)

    def __init__(self, name, password, created_at=None):
        self.name = name
        self.password = password
        if created_at is None:
            self.created_at = datetime.now()
        else:
            self.created_at = created_at

    def __repr__(self):
        return '<Dial Account %s:%s>' % (self.name, self.created_at)

    def get_id(self):
        return unicode(self.id)


class Settings(db.Model):
    """settings for dial or common settings."""
    __tablename__ = 'dial_settings'

    id = db.Column(db.Integer, primary_key=True)
    ipool = db.Column(db.String(80))
    subnet = db.Column(db.String(80))
    c2c = db.Column(db.Boolean)
    duplicate = db.Column(db.Boolean)
    proto = db.Column(db.String(80))

    def __init__(self, ipool, subnet, c2c, duplicate, proto):
        self.ipool = ipool
        self.subnet = subnet
        self.c2c = c2c
        self.duplicate = duplicate
        self.proto = proto

    def __repr__(self):
        return '<Settings %s>' % self.id
