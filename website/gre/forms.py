# -*- coding: utf-8 -*-
"""
    website.tcp.forms
    ~~~~~~~~~~~~~~~~~~~~~~

    vpn forms:
        /tcp/add
"""


from flask.ext.babel import lazy_gettext
from flask_wtf import Form
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired

from website.utils.validators import IP, SubNets


class AddForm(Form):
    local_router_ip = StringField(lazy_gettext("local router ip"),
                                  validators=[DataRequired(message=lazy_gettext("this is required")),
                                              IP()])
    remote_router_ip = StringField(lazy_gettext("remote router ip"),
                                   validators=[DataRequired(message=lazy_gettext("this is required")),
                                               IP()])
    subnet = StringField(lazy_gettext("subnet"),
                         validators=[DataRequired(message=lazy_gettext("this is required")),
                                     SubNets()])
    #: submit button
    create = SubmitField(lazy_gettext("create tunnel"))


class ConsoleForm(Form):
    '''web console form'''
    #: submit button
    ensure = SubmitField(lazy_gettext("ensure"))
    reset = SubmitField(lazy_gettext("reset"))
