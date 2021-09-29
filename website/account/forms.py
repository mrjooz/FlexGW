# -*- coding: utf-8 -*-
"""
    website.account.forms
    ~~~~~~~~~~~~~~~~~~~~~

    account forms:
        /login
        /settings
"""

from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length

from website.account.models import User
from website.utils.validators import ValidOTPCode
from flask.ext.babel import lazy_gettext


class LoginForm(Form):
    account = TextField(lazy_gettext('username'), validators=[
        DataRequired(message=lazy_gettext('this is required.')),
        Length(max=20, message=lazy_gettext('account maximal length is 20.'))
    ])

    password = PasswordField(lazy_gettext('password'), validators=[DataRequired(message=u'this is required.')])

    def validate_password(self, field):
        account = self.account.data
        if not User.check_auth(account, field.data):
            raise ValidationError(lazy_gettext('invalid username/password'))


class MFAForm(Form):
    otp_code = TextField(lazy_gettext('otp code'), validators=[
        DataRequired(message=lazy_gettext('this is required')),
        Length(min=6, max=6, message=lazy_gettext('Length must be 6.')),
        ValidOTPCode()
    ])


class LanguageForm(Form):
    language = SelectField(lazy_gettext("language"),
                           choices=[('en', "English"), ('zh_Hans_CN', u"简体中文")])
