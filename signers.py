# -*- coding: utf-8 -*-

"""
Author: Oliver Zscheyge
Description:
    Signing utilities and creating signers via the Beyond API.
"""

import base64
import hashlib
import hmac

import json
import requests


def sign(message, secret):
    digest = hmac.new(secret.encode('utf-8'),
                      msg=message.encode('utf-8'),
                      digestmod=hashlib.sha1).digest()
    return base64.b64encode(digest).decode('utf-8')


def create_signer(installation):
     return requests.post('%s/payment-method-definitions/%s/payment-method' % (installation.api_url, ""), \
            headers= {
                "Accept": "application/hal+json",
                "Authorization": "Bearer %s" % installation.access_token
            }).status_code
