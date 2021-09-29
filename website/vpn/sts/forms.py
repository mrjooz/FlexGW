# -*- coding: utf-8 -*-
"""
    website.vpn.sts.forms
    ~~~~~~~~~~~~~~~~~~~~~

    vpn forms:
        /vpn/sts/add
        /vpn/sts/<int:id>/settings
"""

from flask.ext.babel import lazy_gettext
from flask_wtf import Form
from wtforms import StringField, TextField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp
from website.utils.validators import SubNets, PublicIP


class AddForm(Form):
    keyexchange = SelectField(lazy_gettext("ike version"),
                              choices=[('ikev1', u'IKEV1'), ('ikev2', u'IKEV2')])

    tunnel_name = StringField(lazy_gettext("tunnel id"),
                              validators=[DataRequired(message=lazy_gettext("this is required")),
                                          Length(max=20, message=lazy_gettext("account maximal length is 20")),
                                          Regexp(r'^[\w]+$', message=lazy_gettext("only contains number, alpha, underline."))])

    start_type = SelectField(lazy_gettext("auto start"),
                             choices=[('add', lazy_gettext("manual")), ('start', lazy_gettext("auto"))])

    negotiation_mode = SelectField(lazy_gettext("negotiation mode"),
                             choices=[('no', lazy_gettext("active")), ('yes', lazy_gettext("aggressive"))])

    dpd_action = SelectField(lazy_gettext("dpd action"),
                             choices=[('none', lazy_gettext("none")), ('clear', lazy_gettext("clear")),
                                      ('hold', lazy_gettext("hold")), ('restart', lazy_gettext("restart"))])

    ike_encryption_algorithm = SelectField(lazy_gettext("ike encryption algorithm"),
                                           choices=[('3des', u'3DES'), ('aes128', u'AES128'),
                                                    ('aes192', u'AES192'), ('aes256', u'AES256')])

    ike_integrity_algorithm = SelectField(lazy_gettext("ike integrity algorithm "),
                                          choices=[('md5', u'MD5'), ('sha1', u'SHA1'),
                                                   ('sha2_256', u'SHA2-256'), ('sha2_384', u'SHA2-384'),
                                                   ('sha2_512', u'SHA2-512'), ('aesxcbc', u'AES-XCBC'),
                                                   ('aescmac', u'AES-CMAC')])

    ike_dh_algorithm = SelectField(lazy_gettext("ike dh algorithm"),
                                   choices=[('modp768', u'Group 1 modp768'), ('modp1024', u'Group 2 modp1024'),
                                            ('modp1536', u'Group 5 modp1536'), ('modp2048', u'Group 14 modp2048'),
                                            ('modp3072', u'Group 15 modp3072'), ('modp4096', u'Group 16 modp4096'),
                                            ('modp6144', u'Group 17 modp6144'), ('modp8192', u'Group 18 modp8192'),
                                            ('ecp256', u'Group 19 ecp256'), ('ecp384', u'Group 20 ecp384'),
                                            ('ecp521', u'Group 21 ecp521'), ('modp1024s160', u'Group 22 modp1024s160'),
                                            ('modp2048s224', u'Group 23 modp2048s224'), ('modp2048s256', u'Group 24 modp2048s256'),
                                            ('ecp192', u'Group 25 ecp192'), ('ecp224', u'Group 26 ecp224'),
                                            ('ecp224bp', u'Group 27 ecp224bp'), ('ecp256bp', u'Group 28 ecp256bp'),
                                            ('ecp384bp', u'Group 29 ecp384bp'), ('ecp512bp', u'Group 30 ecp512bp')])

    esp_encryption_algorithm = SelectField(lazy_gettext("esp encryption algorithm"),
                                           choices=[('3des', u'3DES'), ('aes128', u'AES128'),
                                                    ('aes192', u'AES192'), ('aes256', u'AES256'),
                                                    ('aes128gcm64', u'AES128-GCM64'), ('aes192gcm64', u'AES192-GCM64'),
                                                    ('aes256gcm64', u'AES256-GCM64'), ('aes128gcm96', u'AES128-GCM96'),
                                                    ('aes192gcm96', u'AES192-GCM96'), ('aes256gcm96', u'AES256-GCM96'),
                                                    ('aes128gcm128', u'AES128-GCM128'), ('aes192gcm128', u'AES192-GCM128'),
                                                    ('aes256gcm128', u'AES256-GCM128')])

    esp_integrity_algorithm = SelectField(lazy_gettext("esp integrity algorithm"),
                                          choices=[('md5', u'MD5'), ('sha1', u'SHA1'),
                                                   ('sha2_256', u'SHA2-256'), ('sha2_384', u'SHA2-384'),
                                                   ('sha2_512', u'SHA2-512'), ('aesxcbc', u'AES-XCBC')])

    esp_dh_algorithm = SelectField(lazy_gettext("esp dh algorithm"),
                                   choices=[('null', lazy_gettext("null")),
                                            ('modp768', u'Group 1 modp768'), ('modp1024', u'Group 2 modp1024'),
                                            ('modp1536', u'Group 5 modp1536'), ('modp2048', u'Group 14 modp2048'),
                                            ('modp3072', u'Group 15 modp3072'), ('modp4096', u'Group 16 modp4096'),
                                            ('modp6144', u'Group 17 modp6144'), ('modp8192', u'Group 18 modp8192'),
                                            ('ecp256', u'Group 19 ecp256'), ('ecp384', u'Group 20 ecp384'),
                                            ('ecp521', u'Group 21 ecp521'), ('modp1024s160', u'Group 22 modp1024s160'),
                                            ('modp2048s224', u'Group 23 modp2048s224'), ('modp2048s256', u'Group 24 modp2048s256'),
                                            ('ecp192', u'Group 25 ecp192'), ('ecp224', u'Group 26 ecp224'),
                                            ('ecp224bp', u'Group 27 ecp224bp'), ('ecp256bp', u'Group 28 ecp256bp'),
                                            ('ecp384bp', u'Group 29 ecp384bp'), ('ecp512bp', u'Group 30 ecp512bp')])

    local_subnet = TextAreaField(lazy_gettext("local subnet"),
                                 validators=[DataRequired(message=lazy_gettext("this is required")),
                                             SubNets(message=lazy_gettext("invalid local subnet"))])

    local_id = TextField(lazy_gettext("local id"),
                         validators=[DataRequired(message=lazy_gettext("this is required"))])

    remote_ip = StringField(lazy_gettext("remote ip"),
                            validators=[DataRequired(message=lazy_gettext("this is required")),
                                        PublicIP(message=lazy_gettext("invalid remote ip"))])

    remote_id = TextField(lazy_gettext("remote id"),
                          validators=[DataRequired(message=lazy_gettext("this is required"))])

    remote_subnet = TextAreaField(lazy_gettext("remote subnet"),
                                  validators=[DataRequired(message=lazy_gettext("this is required")),
                                              SubNets(message=lazy_gettext("invalid remote subnet"))])

    psk = StringField(lazy_gettext("psk"),  # '预共享秘钥'
                      validators=[DataRequired(message=lazy_gettext("this is required"))])

    #: submit button
    save = SubmitField(lazy_gettext("save"))
    delete = SubmitField(lazy_gettext("delete"))


class ConsoleForm(Form):
    '''web console form'''
    #: submit button
    stop = SubmitField(lazy_gettext("stop"))
    start = SubmitField(lazy_gettext("start"))
    re_load = SubmitField(lazy_gettext("install&reload"))


class UpDownForm(Form):
    """for tunnel up and down."""
    tunnel_name = StringField(lazy_gettext("tunnel name"))
    #: submit button
    up = SubmitField(lazy_gettext("connect"))
    down = SubmitField(lazy_gettext("disconnect"))
