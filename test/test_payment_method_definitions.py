#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

from payment_method_definitions import read_json_file, system_token, get_payment_method_definitions

CLIENT_ID = os.environ.get('CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET', '')

def test_read_json_file():
    # when
    payment_method_definition = read_json_file('test/beautiful-test-payment.json')

    # then
    assert payment_method_definition.get('_id') == 'beautiful-test-payment'


def test_get_system_access_token():
    # given
    assert len(CLIENT_ID)
    assert len(CLIENT_SECRET)

    # when
    token = system_token(CLIENT_ID, CLIENT_SECRET)

    # then
    assert len(token)
    assert token.count('.') == 2 # JWT has 3 sections


def test_get_payment_method_definitions():
    # given
    token = system_token(CLIENT_ID, CLIENT_SECRET)

    # when
    payment_method_definitions = get_payment_method_definitions(token)

    # then
    _compare_to_expected_payment_method_definitions(payment_method_definitions)

def _compare_to_expected_payment_method_definitions(payment_method_definitions):
    beautiful_test_payment = [pmd for pmd in payment_method_definitions if pmd.get('_id', '') == 'beautiful-test-payment'][0]
    beautiful_test_payment_sandbox = [pmd for pmd in payment_method_definitions if pmd.get('_id', '') == 'beautiful-test-payment-sandbox'][0]
    beautiful_test_payment_embedded = [pmd for pmd in payment_method_definitions if pmd.get('_id', '') == 'beautiful-test-payment-embedded'][0]
    beautiful_test_payment_embedded_on_selection = [pmd for pmd in payment_method_definitions if pmd.get('_id', '') == 'beautiful-test-payment-embedded-selection'][0]

    expected_pmd = read_json_file('test/beautiful-test-payment.json')
    expected_pmd_sandbox = read_json_file('test/beautiful-test-payment-sandbox.json')
    expected_pmd_embedded = read_json_file('test/beautiful-test-payment-embedded.json')
    expected_pmd_embedded_on_selection = read_json_file('test/beautiful-test-payment-embedded-on-selection.json')

    assert expected_pmd == beautiful_test_payment
    assert expected_pmd_sandbox == beautiful_test_payment_sandbox
    assert expected_pmd_embedded == beautiful_test_payment_embedded
    assert expected_pmd_embedded_on_selection == beautiful_test_payment_embedded_on_selection
