# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import superdesk.io.commands.update_ingest as ingest

from unittest import TestCase
from datetime import timedelta
from nose.tools import assert_raises
from superdesk import get_resource_service
from superdesk.utc import utcnow
from superdesk.tests import setup
from superdesk.errors import SuperdeskApiError
from superdesk.io import register_provider
from superdesk.io.tests import setup_providers, teardown_providers
from superdesk.io.ingest_service import IngestService
from superdesk.io.commands.remove_expired_content import get_expired_items


class TestProviderService(IngestService):

    def update(self, provider):
        return []


register_provider('test', TestProviderService())


class UpdateIngestTest(TestCase):
    def setUp(self):
        setup(context=self)
        setup_providers(self)

    def tearDown(self):
        teardown_providers(self)

    def _get_provider(self, provider_name):
        return get_resource_service('ingest_providers').find_one(name=provider_name, req=None)

    def _get_provider_service(self, provider):
        return self.provider_services[provider.get('type')]

    def test_ingest_items(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
        with self.app.app_context():
            provider = self._get_provider(provider_name)
            provider_service = self._get_provider_service(provider)
            provider_service.provider = provider
            items = provider_service.fetch_ingest(guid)
            items.extend(provider_service.fetch_ingest(guid))
            self.assertEquals(12, len(items))
            self.ingest_items(items, provider)

    def test_ingest_item_expiry(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
        with self.app.app_context():
            provider = self._get_provider(provider_name)
            provider_service = self._get_provider_service(provider)
            provider_service.provider = provider
            items = provider_service.fetch_ingest(guid)
            self.assertIsNone(items[1].get('expiry'))
            items[1]['versioncreated'] = utcnow()
            self.ingest_items([items[1]], provider)
            self.assertIsNotNone(items[1].get('expiry'))

    def test_ingest_item_sync_if_missing_from_elastic(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
        with self.app.app_context():
            provider = self._get_provider(provider_name)
            provider_service = self._get_provider_service(provider)
            provider_service.provider = provider
            item = provider_service.fetch_ingest(guid)[0]
            # insert in mongo
            ids = self.app.data._backend('ingest').insert('ingest', [item])
            # check that item is not in elastic
            elastic_item = self.app.data._search_backend('ingest').find_one('ingest', _id=ids[0], req=None)
            self.assertIsNone(elastic_item)
            # trigger sync by fetch
            old_item = get_resource_service('ingest').find_one(_id=ids[0], req=None)
            self.assertIsNotNone(old_item)
            # check that item is synced in elastic
            elastic_item = self.app.data._search_backend('ingest').find_one('ingest', _id=ids[0], req=None)
            self.assertIsNotNone(elastic_item)

    def test_ingest_provider_closed_raises_exception(self):
        provider = {
            'name': 'aap',
            'type': 'aap',
            'is_closed': True,
            'source': 'aap',
            'config': {
                'path': '/'
            }
        }

        with assert_raises(SuperdeskApiError) as error_context:
            aap = self._get_provider_service(provider)
            aap.update(provider)
        ex = error_context.exception
        self.assertTrue(ex.status_code == 500)

    def test_is_scheduled(self):
        self.assertTrue(ingest.is_scheduled({}), 'run after create')
        self.assertFalse(ingest.is_scheduled({'last_updated': utcnow()}), 'wait default time 5m')
        self.assertTrue(ingest.is_scheduled({'last_updated': utcnow() - timedelta(minutes=6)}), 'run after 5m')
        self.assertFalse(ingest.is_scheduled({
            'last_updated': utcnow() - timedelta(minutes=6),
            'update_schedule': {'minutes': 10}
        }), 'or wait if provider has specific schedule')
        self.assertTrue(ingest.is_scheduled({
            'last_updated': utcnow() - timedelta(minutes=11),
            'update_schedule': {'minutes': 10}
        }), 'and run eventually')

    def test_change_last_updated(self):
        with self.app.app_context():
            test_provider = {'type': 'test', '_etag': 'test'}
            self.app.data.insert('ingest_providers', [test_provider])

            ingest.update_provider(test_provider)
            provider = self.app.data.find_one('ingest_providers', req=None, _id=test_provider['_id'])
            self.assertGreaterEqual(utcnow(), provider.get('last_updated'))
            self.assertEqual('test', provider.get('_etag'))

    def test_filter_expired_items(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
        with self.app.app_context():
            provider = get_resource_service('ingest_providers').find_one(name=provider_name, req=None)
            provider_service = self.provider_services[provider.get('type')]
            provider_service.provider = provider
            items = provider_service.fetch_ingest(guid)
            for item in items[:4]:
                item['expiry'] = utcnow() + timedelta(minutes=11)
            self.assertEqual(4, len(ingest.filter_expired_items(provider, items)))

    def test_filter_expired_items_with_no_expiry(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
        with self.app.app_context():
            provider = get_resource_service('ingest_providers').find_one(name=provider_name, req=None)
            provider_service = self.provider_services[provider.get('type')]
            provider_service.provider = provider
            items = provider_service.fetch_ingest(guid)
            self.assertEqual(0, len(ingest.filter_expired_items(provider, items)))

    def test_query_getting_expired_content(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
        with self.app.app_context():
            provider = get_resource_service('ingest_providers').find_one(name=provider_name, req=None)
            provider_service = self.provider_services[provider.get('type')]
            provider_service.provider = provider

            items = provider_service.fetch_ingest(guid)
            for item in items:
                item['ingest_provider'] = str(provider['_id'])

            items[0]['expiry'] = utcnow() - timedelta(minutes=11)
            items[1]['expiry'] = utcnow() + timedelta(minutes=11)
            items[2]['expiry'] = utcnow() + timedelta(minutes=11)
            items[5]['versioncreated'] = utcnow() + timedelta(minutes=11)

            self.app.data.insert('ingest', items)
            expiredItems = get_expired_items(str(provider['_id']), utcnow() - timedelta(minutes=2880))
            self.assertEquals(3, expiredItems.count())

    def test_apply_rule_set(self):
        with self.app.app_context():
            item = {'body_html': '@@body@@'}

            provider_name = 'reuters'
            provider = self._get_provider(provider_name)
            self.assertEquals('body', ingest.apply_rule_set(item, provider)['body_html'])

            item = {'body_html': '@@body@@'}
            provider_name = 'AAP'
            provider = self._get_provider(provider_name)
            self.assertEquals('@@body@@', ingest.apply_rule_set(item, provider)['body_html'])

    def test_all_ingested_items_have_sequence(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
        with self.app.app_context():
            provider = self._get_provider(provider_name)
            provider_service = self._get_provider_service(provider)
            provider_service.provider = provider
            item = provider_service.fetch_ingest(guid)[0]
            get_resource_service("ingest").set_ingest_provider_sequence(item, provider)
            self.assertIsNotNone(item['ingest_provider_sequence'])

    def test_get_task_ttl(self):
        self.assertEquals(300, ingest.get_task_ttl({}))
        provider = {'update_schedule': {'minutes': 10}}
        self.assertEquals(600, ingest.get_task_ttl(provider))
        provider['update_schedule']['hours'] = 1
        provider['update_schedule']['minutes'] = 1
        self.assertEquals(3660, ingest.get_task_ttl(provider))

    def test_get_task_id(self):
        provider = {'name': 'foo', '_id': 'abc'}
        self.assertEquals('update-ingest-foo-abc', ingest.get_task_id(provider))

    def test_is_idle(self):
        provider = dict(idle_time=dict(hours=1, minutes=0))
        provider['last_item_update'] = utcnow()
        self.assertEquals(ingest.get_is_idle(provider), False)
        provider['idle_time']['hours'] = -1
        self.assertEquals(ingest.get_is_idle(provider), True)
        provider['idle_time'] = dict(hours=0, minutes=0)
        self.assertEquals(ingest.get_is_idle(provider), False)
