# -*- coding: utf-8 -*-

"""
Author: Oliver Zscheyge
Description:
    Web app that generates beautiful order documents for ePages Beyond shops.
"""

import os
import logging
import random
from urllib.parse import urlencode, urlparse, unquote

from flask import Flask, render_template, request, Response, abort, escape, jsonify

from app_installations import AppInstallations, PostgresAppInstallations
from shops import Shop, PostgresShops, get_shop_id
from payment_method_definitions import create_payment_method
from signers import sign

app = Flask(__name__)

APP_INSTALLATIONS = None
SHOPS = None
CLIENT_SECRET = ''
DEFAULT_HOSTNAME = ''
LOGGER = logging.getLogger("app")

AUTO_INSTALLED_PAYMENT_METHOD_DEFINITIONS = ["beautiful-test-payment-embedded"]

@app.route('/')
def root():
    if DEFAULT_HOSTNAME != '':
        return render_template('index.html', installed=True, hostname=DEFAULT_HOSTNAME)
    return render_template('index.html', installed=False)


@app.route('/<hostname>')
def root_hostname(hostname):
    return render_template('index.html', installed=True, hostname=hostname)

@app.route('/callback')
def callback():
    args = request.args
    return_url = args.get("return_url")
    access_token_url = args.get("access_token_url")
    api_url = args.get("api_url")
    code = args.get("code")
    signature = unquote(args.get("signature"))

    APP_INSTALLATIONS.retrieve_token_from_auth_code(api_url, code, access_token_url, signature)

    hostname = urlparse(api_url).hostname
    installation = get_installation(hostname)

    created_payment_methods = _auto_create_payment_methods(installation)
    _get_and_store_shop_id(installation)

    return render_template('callback_result.html',
                            return_url=return_url,
                            created_payment_methods=created_payment_methods)

def _auto_create_payment_methods(installation):
    created_payment_methods = []
    for pmd_name in AUTO_INSTALLED_PAYMENT_METHOD_DEFINITIONS:
        status = create_payment_method(installation, pmd_name)
        created_payment_methods.append({
            "status_code": status,
            "payment_method_definition_name": pmd_name
        })
        print("Created payment method for %s in shop %s with status %i" % (pmd_name, installation.hostname, status))

    return created_payment_methods

def _get_and_store_shop_id(installation):
    shop_id = get_shop_id(installation)
    shop = Shop(shop_id, installation.hostname)
    SHOPS.create_or_update_shop(shop)

@app.route('/merchants/<shop_id>')
def merchant_account_status(shop_id):
    print("Serving always ready merchant account status")
    return jsonify({
        "ready" : True,
        "details" : {
            "primaryEmail" : "example@b.c"
        }
    })

@app.route('/payments', methods=['POST'])
def create_payment():
    print("Creating payment with paymentNote")
    return jsonify({
        "paymentNote": "Please transfer the money using the reference %s to the account %s" % (generate_id(), generate_id()),
    })

@app.route('/embedded-payments', methods=['POST'])
def create_embedded_payment():
    app_hostname = urlparse(request.url_root).hostname

    payload = request.get_json(force=True)
    shop = payload.get('shop', {}).get('name', '')
    payment_id = payload.get('paymentId', '')
    signature = sign(payment_id, CLIENT_SECRET)

    params = {
        'paymentId': payment_id,
        'signature': signature,
        'shop': shop
    }
    embeddedApprovalUri = 'https://%s/embedded-payment-approval?%s' % (app_hostname, urlencode(params))
    print('Created embedded payment for shop %s' % shop)
    return jsonify({
        'embeddedApprovalUri': embeddedApprovalUri
    })

@app.route('/embedded-payment-approval')
def embedded_payment_approval():
    args = request.args
    payment_id = unquote(args.get('paymentId', ''))
    signature = unquote(args.get('signature', ''))
    shop = unquote(args.get('shop', ''))
    approve_uri = '/payments/%s/approve' % payment_id
    cancel_uri = '/payments/%s/cancel' % payment_id
    return render_template('embedded_payment_approval.html',
                           state='PENDING',
                           payment_id=payment_id,
                           signature=signature,
                           shop=shop,
                           approve_uri=approve_uri,
                           cancel_uri=cancel_uri)

@app.route('/payments/<payment_id>/approve', methods=['POST'])
def approve_payment(payment_id):
    ''' Currently only needed for embedded payments
    '''
    print('Approving payment %s' % payment_id)
    return render_template('embedded_payment_approval.html',
                           state='APPROVED',
                           payment_id=payment_id)

@app.route('/payments/<payment_id>/cancel', methods=['POST'])
def cancel_payment(payment_id):
    ''' Currently only needed for embedded payments
    '''
    print('Canceling payment %s' % payment_id)
    return render_template('embedded_payment_approval.html',
                           state='CANCELED',
                           payment_id=payment_id)

@app.route('/payments/<payment_id>/capture', methods=['POST'])
def capture_payment(payment_id):
    print("Capturing payment %s" % payment_id)
    return jsonify({
        "paymentStatus" : "CAPTURED",
    })

def generate_id():
    return ''.join(random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))

@app.before_request
def limit_open_proxy_requests():
    """Security measure to prevent:
    http://serverfault.com/questions/530867/baidu-in-nginx-access-log
    http://security.stackexchange.com/questions/41078/url-from-another-domain-in-my-access-log
    http://serverfault.com/questions/115827/why-does-apache-log-requests-to-get-http-www-google-com-with-code-200
    http://stackoverflow.com/questions/22251038/how-to-limit-flask-dev-server-to-only-one-visiting-ip-address
    """
    if not is_allowed_request():
        print("Someone is messing with us:")
        print(request.url_root)
        print(request)
        abort(403)

def is_allowed_request():
    url = request.url_root
    return '.herokuapp.com' in url or \
           '.ngrok.io' in url or \
           'localhost:8080' in url or \
           '127.0.0' in url or \
           '0.0.0.0:80' in url

def get_installation(hostname):
    installation = APP_INSTALLATIONS.get_installation(hostname)
    if not installation:
        raise ShopNotKnown(hostname)
    return installation

@app.errorhandler(404)
def page_not_found(e):
    return '<h1>404 File Not Found! :(</h1>', 404

class ShopNotKnown(Exception):
    def __init__(self, hostname):
        super()
        self.hostname = hostname

@app.errorhandler(ShopNotKnown)
def shop_not_known(e):
    return render_template('index.html', installed=False, error_message="App not installed for the requested shop with hostname %s" % e.hostname)

@app.errorhandler(Exception)
def all_exception_handler(error):
    LOGGER.exception(error)
    return 'Error', 500

def init():
    global APP_INSTALLATIONS
    global SHOPS
    global DEFAULT_HOSTNAME
    global CLIENT_SECRET

    CLIENT_ID = os.environ.get('CLIENT_ID', '')
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET', '')

    print("Initialize PostgresAppInstallations")
    APP_INSTALLATIONS = PostgresAppInstallations(os.environ.get('DATABASE_URL'), CLIENT_ID, CLIENT_SECRET)
    APP_INSTALLATIONS.create_schema()

    print("Initialize PostgresShops")
    SHOPS = PostgresShops(os.environ.get('DATABASE_URL'))
    SHOPS.create_schema()

init()
if __name__ == '__main__':
    app.run()
