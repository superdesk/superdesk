# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from httmock import urlmatch, HTTMock
from urllib.parse import parse_qs
from os.path import os, basename


@urlmatch(scheme='https', netloc='commerce.reuters.com', path='/rmd/rest/xml/login')
def login_request(url, request):
    return {'status_code': 200,
            'content': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><authToken>fake_token</authToken>'}


@urlmatch(scheme='http', netloc='rmb.reuters.com', path='/rmd/rest/xml/item')
def item_request(url, request):
    try:
        params = parse_qs(url.query, keep_blank_values=True)
        fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        file = os.path.join(fixtures, params['id'][0])
        with open(file, "r") as stored_response:
            content = stored_response.read()
            return {'status_code': 200, 'content': content}
    except Exception:
        return {'status_code': 404}


@urlmatch(scheme='http', netloc='content.reuters.com')
def content_request(url, request):
    try:
        fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        file = os.path.join(fixtures, basename(url.path))
        with open(file, 'rb') as stored_response:
            content = stored_response.read()
            return {'status_code': 200, 'content': content}
    except Exception:
        return {'status_code': 404}


def setup_reuters_mock(context):
    context.mock = HTTMock(*[login_request, item_request, content_request])
    context.mock.__enter__()


def teardown_reuters_mock(context):
    if hasattr(context, 'mock'):
        context.mock.__exit__(None, None, None)
