# -*- coding: utf-8 -*-

"""
Author: Oliver Zscheyge
Description:
    Signing utilities.
"""

import base64
import hashlib
import hmac

def sign(message, secret):
    digest = hmac.new(secret.encode('utf-8'),
                      msg=message.encode('utf-8'),
                      digestmod=hashlib.sha1).digest()
    return base64.b64encode(digest).decode('utf-8')
