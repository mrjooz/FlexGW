# -*- coding: utf-8 -*-
"""
    website.account.services
    ~~~~~~~~~~~~~~~~~~~~~~~~

    account login validate.
"""

import pyotp
import qrcode

from website import db, login_manager
from website.account.models import User
from website.account.models import UserDetails


@login_manager.user_loader
def load_user(user_id):
    return User.query_filter_by(id=user_id)


def get_mfa_qr_code(username):
    user_details = UserDetails.query.get(username)
    if user_details is None:
        user_details = UserDetails(username, pyotp.random_base32())
        db.session.add(user_details)
        db.session.commit()

    if user_details.otp_key is None:
        UserDetails.query.filter(UserDetails.username == username).update({"otp_key":  pyotp.random_base32()})
        db.session.commit()
        user_details = UserDetails.query.get(username)

    totp = pyotp.TOTP(user_details.otp_key)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(totp.provisioning_uri(user_details.username, "FlexGW"))
    qr.make(fit=True)
    img = qr.make_image()
    return img
