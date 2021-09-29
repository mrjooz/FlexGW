# -*- coding: utf-8 -*-
"""
    website.tcp.forms
    ~~~~~~~~~~~~~~~~~~~~~~

    vpn forms:
        /tcp/add
"""


from flask.ext.babel import lazy_gettext
from flask_wtf import Form
from wtforms import IntegerField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from website.utils.validators import IP
from website.utils.validators import PortInUse


class AddForm(Form):
    local_port = IntegerField(lazy_gettext("local port"),
                              validators=[DataRequired(message=lazy_gettext("this is required")),
                                          PortInUse()])
    dest_ip = StringField(lazy_gettext("destination ip"),
                          validators=[DataRequired(message=lazy_gettext("this is required")),
                                      IP()])
    dest_port = IntegerField(lazy_gettext("destination port"),
                             validators=[DataRequired(message=lazy_gettext("this is required"))])
    #: submit button
    create = SubmitField(lazy_gettext("create tunnel"))


class ConsoleForm(Form):

    '''web console form'''
    #: submit button
    ensure = SubmitField(lazy_gettext("ensure"))
    reset = SubmitField(lazy_gettext("reset"))
