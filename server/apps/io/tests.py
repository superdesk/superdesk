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
from superdesk.io.commands.update_ingest import ingest_items
from .reuters_mock import setup_reuters_mock, teardown_reuters_mock
from .reuters import ReutersIngestService
from .aap import AAPIngestService
from superdesk.io.teletype import TeletypeIngestService
from .dpa import DPAIngestService
import superdesk


def setup_providers(context):
    app = context.app
    context.providers = {}
    context.provider_services = {}
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
        providers = [
            {'name': 'reuters', 'type': 'reuters', 'source': 'reuters', 'is_closed': False, 'rule_set': result[0],
             'config': {'username': app.config['REUTERS_USERNAME'],
                        'password': app.config['REUTERS_PASSWORD']}},
            {'name': 'AAP', 'type': 'aap', 'source': 'AAP Ingest', 'is_closed': False,
             'config': {'path': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')},
             'critical_errors': {'2005': True}},
            {'name': 'teletype', 'type': 'teletype', 'source': 'AAP Teletype', 'is_closed': False,
             'config': {'path': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')}},
            {'name': 'DPA', 'type': 'dpa', 'source': 'DPA', 'is_closed': False,
             'config': {'path': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')}}
        ]

        result = superdesk.get_resource_service('ingest_providers').post(providers)
        context.providers['reuters'] = result[0]
        context.providers['aap'] = result[1]
        context.provider_services['reuters'] = ReutersIngestService()
        context.provider_services['aap'] = AAPIngestService()
        context.provider_services['teletype'] = TeletypeIngestService()
        context.provider_services['dpa'] = DPAIngestService()


def teardown_providers(context):
    teardown_reuters_mock(context)
