# -*- coding: utf-8 -*-

import requests

def approve_payment(installation, payment_id):
    return \
        requests.post('%s/payments/%s/approve' % (installation.api_url, payment_id), \
                 headers={
                     "Accept": "application/hal+json",
                     "Authorization": "Bearer %s" % installation.access_token
                 }).json() \
        .get('returnUri', None)

def cancel_payment(installation, payment_id):
    return \
        requests.post('%s/payments/%s/cancel' % (installation.api_url, payment_id), \
                 headers={
                     "Accept": "application/hal+json",
                     "Authorization": "Bearer %s" % installation.access_token
                 }).json() \
        .get('returnUri', None)
