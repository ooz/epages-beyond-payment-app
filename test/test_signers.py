#!/usr/bin/env python
# -*- coding: utf-8 -*-

from signers import sign

def test_sign():
    signature = sign('Hello, unaltered message!', 'ha2e25nfmvo1dgeqsncd3nqsoj')
    assert signature == 'WJZWs4v/Vgru4X6hdKhI71TmhUM='
