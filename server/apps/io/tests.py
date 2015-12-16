# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os

import superdesk
from superdesk.io.commands.update_ingest import ingest_items
from .reuters_mock import setup_reuters_mock, teardown_reuters_mock


def setup_providers(context):
    app = context.app
    context.providers = {}
    context.ingest_items = ingest_items
    with app.test_request_context(app.config['URL_PREFIX']):
        rule_sets = {'name': 'reuters_rule_sets',
                     'rules': [
                         {"old": "@", "new": ""},
                     ]}

        result = superdesk.get_resource_service('rule_sets').post([rule_sets])

        app.config['REUTERS_USERNAME'] = 'no_username'
        app.config['REUTERS_PASSWORD'] = 'no_password'
        setup_reuters_mock(context)

        path_to_fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        providers = [
            {'name': 'reuters', 'source': 'reuters', 'feeding_service': 'reuters_http', 'feed_parser': 'newsml2',
             'is_closed': False, 'rule_set': result[0],
             'config': {'url': 'http://rmb.reuters.com/rmd/rest/xml',
                        'auth_url': 'https://commerce.reuters.com/rmd/rest/xml/login',
                        'username': app.config['REUTERS_USERNAME'], 'password': app.config['REUTERS_PASSWORD']}},
            {'name': 'AAP', 'source': 'AAP Ingest', 'feeding_service': 'file', 'feed_parser': 'nitf',
             'is_closed': False, 'critical_errors': {'2005': True}, 'config': {'path': path_to_fixtures}},
            {'name': 'teletype', 'source': 'AAP Teletype', 'feeding_service': 'file', 'feed_parser': 'zczc',
             'is_closed': False, 'config': {'path': path_to_fixtures}},
            {'name': 'DPA', 'source': 'DPA', 'feeding_service': 'file', 'feed_parser': 'dpa_iptc7901',
             'is_closed': False, 'config': {'path': path_to_fixtures}}
        ]

        result = superdesk.get_resource_service('ingest_providers').post(providers)
        context.providers['reuters'] = result[0]
        context.providers['aap'] = result[1]
        context.providers['teletype'] = result[2]
        context.providers['dpa'] = result[3]


def teardown_providers(context):
    teardown_reuters_mock(context)
