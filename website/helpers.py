# -*- coding: utf-8 -*-
"""
    website.helpers
    ~~~~~~~~~~~~~~~

    top level helpers.
"""


from flask import request


def log_request(sender, **extra):
    sender.logger.info('[Request Message]: %s %s %s',
                       request.method,
                       request.url,
                       request.data)


def log_exception(sender, exception, **extra):
    sender.logger.error('[Exception Request]: %s', exception)


def to_dict(sqlalchemy_object):
    d = {}
    for column in sqlalchemy_object.__table__.columns:
        d[column.name] = getattr(sqlalchemy_object, column.name)

    return d
