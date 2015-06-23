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
from datetime import timedelta
from superdesk.tests import TestCase
import superdesk
from superdesk.utc import utcnow
from .reuters_token import get_token
from .reuters import ReutersIngestService
from settings import URL_PREFIX


def setup_provider(token, hours):
    return {
        'name': ReutersIngestService.PROVIDER,
        'type': ReutersIngestService.PROVIDER,
        'source': ReutersIngestService.PROVIDER,
        'content_expiry': 2880,
        'token': {
            'token': token,
            'created': utcnow() - timedelta(hours=hours),
        }
    }


class GetTokenTestCase(TestCase):

    def test_get_null_token(self):
        provider = {}
        self.assertEquals('', get_token(provider))

    def test_get_existing_token(self):
        provider = setup_provider('abc', 10)
        self.assertEquals('abc', get_token(provider))

    def test_get_expired_token(self):
        """Expired is better than none.."""
        provider = setup_provider('abc', 24)
        self.assertEquals('abc', get_token(provider))

    def test_fetch_token(self):
        with self.app.test_request_context(URL_PREFIX):
            provider = setup_provider('abc', 24)
            superdesk.get_resource_service('ingest_providers').post([provider])
            self.assertTrue(provider.get('_id'))
            provider['config'] = {}
            provider['config']['username'] = os.environ.get('REUTERS_USERNAME', '')
            provider['config']['password'] = os.environ.get('REUTERS_PASSWORD', '')
            if provider['config']['username']:
                token = get_token(provider, update=True)
                self.assertNotEquals('', token)
                self.assertEquals(token, provider['token']['token'])

                dbprovider = superdesk.get_resource_service('ingest_providers').find_one(
                    type=ReutersIngestService.PROVIDER, req=None)
                self.assertEquals(token, dbprovider['token']['token'])
