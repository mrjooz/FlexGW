# -*- coding: utf-8 -*-
"""
    website.vpn.dial.forms
    ~~~~~~~~~~~~~~~~~~~~~~

    vpn forms:
        /vpn/dial/add
        /vpn/dial/settings
        /vpn/dial/<int:id>/settings
"""


from flask.ext.babel import lazy_gettext
from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Regexp
from website.utils.validators import SubNets, IPool


class AddForm(Form):
    name = StringField(lazy_gettext("account"),
                       validators=[DataRequired(message=lazy_gettext("this is required")),
                                   Length(max=20, message=lazy_gettext("account maximal length is 20")),
                                   Regexp(r'^[\w]+$', message=lazy_gettext("only contains number, alpha, underline."))])
    password = StringField(lazy_gettext("password"),
                           validators=[DataRequired(message=lazy_gettext("this is required")),
                                       Length(max=20, message=lazy_gettext("password maximal length is 20")),
                                       Regexp(r'^[\w]+$', message="only contains number, alpha, underline.")])
    #: submit button
    save = SubmitField(lazy_gettext("save"))
    delete = SubmitField(lazy_gettext("delete"))


class SettingsForm(Form):
    ipool = StringField(lazy_gettext("ip pool"),
                        validators=[DataRequired(message=lazy_gettext("this is required")),
                                    IPool(message=lazy_gettext("invalid ip pool"))])
    subnet = TextAreaField(lazy_gettext("subnets"),
                           validators=[DataRequired(message=lazy_gettext("this is required")),
                                       SubNets(message=lazy_gettext("invalid subnets"))])
    c2c = SelectField(lazy_gettext("allow communicate between clients"),
                      choices=[('no', lazy_gettext("no")), ('yes', lazy_gettext("yes"))])
    duplicate = SelectField(lazy_gettext("allow multi login using one account"),
                            choices=[('no', lazy_gettext("no")), ('yes', lazy_gettext("yes"))])
    proto = SelectField(lazy_gettext("protocol"),
                        choices=[('udp', u'UDP'), ('tcp', u'TCP')])


class ConsoleForm(Form):
    '''web console form'''
    #: submit button
    stop = SubmitField(lazy_gettext("close"))
    start = SubmitField(lazy_gettext("start"))
    re_load = SubmitField(lazy_gettext("install&reload"))
