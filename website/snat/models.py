# -*- coding: utf-8 -*-
"""
    website.snat.models
    ~~~~~~~~~~~~~~~~~~~~~~~

"""

from website import db


class SNAT(db.Model):

    '''SNAT infomation.'''
    __tablename__ = 'snat_rule'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source = db.Column(db.String(30), nullable=False)
    gateway = db.Column(db.String(30), nullable=False)

    def __init__(self, source, gateway):
        self.source = source
        self.gateway = gateway
