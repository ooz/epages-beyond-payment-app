# -*- coding: utf-8 -*-

import json
import requests

SYSTEM_API_URL = "https://system.beyondshop.cloud/api"

PAYMENT_METHOD_DEFINITION_ID = ""

def read_json_file(file_path):
    data = {}
    with open(file_path) as f:
        data = json.load(f)
    return data

def system_token(client_id, client_secret):
    return requests.post('%s/oauth/token' % SYSTEM_API_URL, auth=(client_id, client_secret), data={"grant_type": "client_credentials"}) \
        .json() \
        .get("access_token", "")

def create_payment_method(installation):
    pass
    """
    requests.post(url=token_url, data=params, auth=(self.client_id, self.client_secret)).json()

    order_json = requests.get(installation.api_url + "payment-method-definitions/testPMD/payment-method" % order_id, \
        headers={"AUTHORIZATION": "Bearer %s" % installation.access_token})
    """

def get_payment_method_definitions(system_token):
    payment_method_definitions = \
        requests.get('%s/payment-method-definitions' % SYSTEM_API_URL, \
                 headers={
                     "Accept": "application/hal+json",
                     "Authorization": "Bearer %s" % system_token
                 }).json().get("_embedded", {}).get("payment-method-definitions", [])

    return payment_method_definitions

def create_payment_method_definition(system_token, file_path):
    payment_method_definition_create_payload = read_json_file(file_path)

    created_payment_method_definition = \
        requests.post('%s/payment-method-definitions' % SYSTEM_API_URL, \
            headers= {
                "Accept": "application/hal+json",
                "Content-Type": "application/json",
                "Authorization": "Bearer %s" % system_token
            }, \
            json=payment_method_definition_create_payload).json()
    return created_payment_method_definition
