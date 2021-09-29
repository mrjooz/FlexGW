#!/usr/bin/env python
# coding=utf-8

import pyotp
import socket

from flask import session
from flask.ext.login import current_user
from flask.ext.babel import lazy_gettext

from wtforms import ValidationError

from website.account.models import UserDetails


def ValidOTPCode(message=lazy_gettext("OTP Code incorrect.")):
    def _valid_otp_code(form, field):
        value = field.data
        username = ""
        if "temp_username" in session:
            username = session['temp_username']
        else:
            username = current_user.username

        user_details = UserDetails.query.get(username)
        totp = pyotp.TOTP(user_details.otp_key)
        if not totp.verify(value):
            raise ValidationError(message)
        else:
            return True
    return _valid_otp_code


def IP(message=lazy_gettext("invalid ip.")):
    def _ip(form, field):
        value = field.data
        parts = value.split('.')
        if len(parts) == 4 and all(x.isdigit() for x in parts):
            numbers = list(int(x) for x in parts)
            if not all(num >= 0 and num < 256 for num in numbers):
                raise ValidationError(message)
            return True
        raise ValidationError(message)
    return _ip


def _ipool(value):
    try:
        ip = value.split('/')[0]
        mask = int(value.split('/')[1])
    except:
        return False
    if mask < 0 or mask > 32:
        return False
    parts = ip.split('.')
    if len(parts) == 4 and all(x.isdigit() for x in parts):
        numbers = list(int(x) for x in parts)
        if not all(num >= 0 and num < 256 for num in numbers):
            return False
        return True
    return False


def SubNets(message=lazy_gettext("invalid subnet.")):
    def __subnets(form, field):
        value = field.data
        parts = [i.strip() for i in value.split(',')]
        if not all(_ipool(part) for part in parts):
            raise ValidationError(message)
    return __subnets


def IPorNet(message=lazy_gettext("invalid ip or subnet.")):
    def _ipornet(form, field):
        value = field.data
        ip = value.split('/')[0]
        if '/' in value:
            try:
                mask = int(value.split('/')[1])
            except:
                raise ValidationError(message)
            if mask < 0 or mask > 32:
                    raise ValidationError(message)
        parts = ip.split('.')
        if len(parts) == 4 and all(x.isdigit() for x in parts):
            numbers = list(int(x) for x in parts)
            if not all(num >= 0 and num < 256 for num in numbers):
                raise ValidationError(message)
            return True
        raise ValidationError(message)
    return _ipornet


def PortInUse(message=lazy_gettext("port in use.")):
    def _ip(form, field):
        value = field.data
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("", value))
            return True
        except:
            raise ValidationError(message)
        finally:
            s.close()
    return _ip


def PublicIP(message=lazy_gettext("invalid public ip")):
    def _publicip(form, field):
        value = field.data
        parts = value.split('.')
        if len(parts) == 4 and all(x.isdigit() for x in parts):
            numbers = list(int(x) for x in parts)
            if numbers[0] == 10:
                raise ValidationError(message)
            elif numbers[0] == 100 and numbers[1] >= 64 and numbers[1] <= 127:
                raise ValidationError(message)
            elif numbers[0] == 192 and numbers[1] == 168:
                raise ValidationError(message)
            elif numbers[0] == 172 and numbers[1] >= 16 and numbers[1] <= 31:
                raise ValidationError(message)
            elif not all(num >= 0 and num < 256 for num in numbers):
                raise ValidationError(message)
            return True
        raise ValidationError(message)
    return _publicip


def IPool(message=lazy_gettext("invalid ip pool")):
    def __ipool(form, field):
        value = field.data
        if not _ipool(value):
            raise ValidationError(message)
    return __ipool
