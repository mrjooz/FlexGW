# -*- coding: utf-8 -*-
"""
    website.account.models
    ~~~~~~~~~~~~~~~~~~~~~~

    account system models.
"""


import sys

from simplepam import authenticate

from flask import current_app

from website import db
from website.services import exec_command


class User(object):

    id = None
    username = None

    def __init__(self, id, username):
        self.id = id
        self.username = username

    def __repr__(self):
        return '<User {0}:{1}>'.format(self.id, self.username)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    @classmethod
    def query_filter_by(cls, id=None, username=None):
        if id:
            cmd = ['getent', 'passwd', str(id)]
        elif username:
            cmd = ['id', '-u', str(username)]
        else:
            return None
        try:
            r = exec_command(cmd)
        except:
            current_app.logger.error('[Account System]: exec_command error: %s:%s', cmd,
                                     sys.exc_info()[1])
            return None
        if r['return_code'] != 0:
            current_app.logger.error('[Account System]: exec_command return: %s:%s:%s',
                                     cmd, r['return_code'], r['stderr'])
            return None
        if id:
            username = r['stdout'].split(':')[0]
            return cls(id, username)
        if username:
            id = int(r['stdout'])
            return cls(id, username)

    @classmethod
    def check_auth(cls, username, password):
        r = authenticate(str(username), str(password), service='sshd')
        if not r:
            current_app.logger.error('[Account System]: %s pam auth failed return: %s',
                                     username, r)
        return r


class UserDetails(db.Model):

    '''user details.'''
    __tablename__ = 'user_details'

    username = db.Column(db.String(80), primary_key=True)
    otp_key = db.Column(db.String(16))
    otp_enabled = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(10), default="en")

    def __init__(self, username, otp_key=None, otp_enabled=False, language=None):
        self.username = username
        self.otp_key = otp_key
        self.otp_enabled = otp_enabled
        if language is None:
            self.language = current_app.config['BABEL_DEFAULT_LOCALE']
        else:
            self.language = language

    def __repr__(self):
        return '<User Detail %s>' % self.name

    def get_id(self):
        return unicode(self.username)
