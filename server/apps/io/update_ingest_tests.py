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
from datetime import timedelta
from nose.tools import assert_raises
from superdesk import get_resource_service
from superdesk.utc import utcnow
from superdesk.errors import SuperdeskApiError, ProviderError
from superdesk.io import register_provider
from .tests import setup_providers, teardown_providers
from superdesk.io.ingest_service import IngestService
from superdesk.io.commands.remove_expired_content import get_expired_items, RemoveExpiredContent
from superdesk.celery_task_utils import mark_task_as_not_running, is_task_running
from test_factory import SuperdeskTestCase


class TestProviderService(IngestService):

    def update(self, provider):
        return []


register_provider('test', TestProviderService(), [ProviderError.anpaError(None, None).get_error_description()])


class CeleryTaskRaceTest(SuperdeskTestCase):

    def test_the_second_update_fails_if_already_running(self):
        provider = {'_id': 'abc', 'name': 'test provider', 'update_schedule': {'minutes': 1}}
        removed = mark_task_as_not_running(provider['name'], provider['_id'])
        self.assertFalse(removed)

        failed_to_mark_as_running = is_task_running(provider['name'], provider['_id'], {'minutes': 1})
        self.assertFalse(failed_to_mark_as_running, 'Failed to mark ingest update as running')

        failed_to_mark_as_running = is_task_running(provider['name'], provider['_id'], {'minutes': 1})
        self.assertTrue(failed_to_mark_as_running, 'Ingest update marked as running, possible race condition')

        removed = mark_task_as_not_running(provider['name'], provider['_id'])
        self.assertTrue(removed, 'Failed to mark ingest update as not running.')


class UpdateIngestTest(SuperdeskTestCase):

    def setUp(self):
        super().setUp()
        setup_providers(self)

    def tearDown(self):
        super().tearDown()
        teardown_providers(self)

    def _get_provider(self, provider_name):
        return get_resource_service('ingest_providers').find_one(name=provider_name, req=None)

    def _get_provider_service(self, provider):
        return self.provider_services[provider.get('type')]

    def test_ingest_items(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
        provider = self._get_provider(provider_name)
        provider_service = self._get_provider_service(provider)
        provider_service.provider = provider
        items = provider_service.fetch_ingest(guid)
        items.extend(provider_service.fetch_ingest(guid))
        self.assertEqual(12, len(items))
        self.ingest_items(items, provider)

    def test_ingest_item_expiry(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
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

    def test_ingest_provider_closed_when_critical_error_raised(self):
        provider_name = 'AAP'
        provider = self._get_provider(provider_name)
        self.assertFalse(provider.get('is_closed'))
        provider_service = self._get_provider_service(provider)
        provider_service.provider = provider
        provider_service.close_provider(provider, ProviderError.anpaError())
        provider = self._get_provider(provider_name)
        self.assertTrue(provider.get('is_closed'))

    def test_ingest_provider_calls_close_provider(self):
        def mock_update(provider):
            raise ProviderError.anpaError()

        provider_name = 'AAP'
        provider = self._get_provider(provider_name)
        self.assertFalse(provider.get('is_closed'))
        provider_service = self._get_provider_service(provider)
        provider_service.provider = provider
        provider_service._update = mock_update
        with assert_raises(ProviderError):
            provider_service.update(provider)
        provider = self._get_provider(provider_name)
        self.assertTrue(provider.get('is_closed'))

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
        ingest_provider = {'name': 'test', 'type': 'test', '_etag': 'test'}
        self.app.data.insert('ingest_providers', [ingest_provider])

        ingest.update_provider(ingest_provider)
        provider = self.app.data.find_one('ingest_providers', req=None, _id=ingest_provider['_id'])
        self.assertGreaterEqual(utcnow(), provider.get('last_updated'))
        self.assertEqual('test', provider.get('_etag'))

    def test_filter_expired_items(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
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
        provider = get_resource_service('ingest_providers').find_one(name=provider_name, req=None)
        provider_service = self.provider_services[provider.get('type')]
        provider_service.provider = provider
        items = provider_service.fetch_ingest(guid)
        self.assertEqual(0, len(ingest.filter_expired_items(provider, items)))

    def test_query_getting_expired_content(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
        provider = get_resource_service('ingest_providers').find_one(name=provider_name, req=None)
        provider_service = self.provider_services[provider.get('type')]
        provider_service.provider = provider

        items = provider_service.fetch_ingest(guid)
        now = utcnow()
        for i, item in enumerate(items):
            item['ingest_provider'] = provider['_id']
            expiry_time = now - timedelta(hours=11)
            if i > 4:
                expiry_time = now + timedelta(minutes=11)

            item['expiry'] = item['versioncreated'] = expiry_time

        service = get_resource_service('ingest')
        service.post(items)
        expiredItems = get_expired_items(provider, now)
        self.assertEqual(5, expiredItems.count())

    def test_expiring_with_content(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
        provider = get_resource_service('ingest_providers').find_one(name=provider_name, req=None)
        provider_service = self.provider_services[provider.get('type')]
        provider_service.provider = provider

        items = provider_service.fetch_ingest(guid)
        now = utcnow()
        for i, item in enumerate(items):
            item['ingest_provider'] = provider['_id']
            expiry_time = now - timedelta(hours=11)
            if i > 4:
                expiry_time = now + timedelta(minutes=11)

            item['expiry'] = item['versioncreated'] = expiry_time

        service = get_resource_service('ingest')
        service.post(items)

        # ingest the items and expire them
        self.ingest_items(items, provider)
        before = service.get(req=None, lookup={})
        self.assertEqual(6, before.count())

        remove = RemoveExpiredContent()
        remove.run(provider.get('type'))

        # only one left in ingest
        after = service.get(req=None, lookup={})
        self.assertEqual(1, after.count())

    def test_expiring_content_with_files(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
        provider = get_resource_service('ingest_providers').find_one(name=provider_name, req=None)
        provider_service = self.provider_services[provider.get('type')]
        provider_service.provider = provider

        items = provider_service.fetch_ingest(guid)
        for item in items:
            item['ingest_provider'] = provider['_id']

        now = utcnow()
        items[0]['expiry'] = now - timedelta(hours=11)
        items[1]['expiry'] = now - timedelta(hours=11)
        items[2]['expiry'] = now + timedelta(hours=11)
        items[5]['versioncreated'] = now + timedelta(minutes=11)

        service = get_resource_service('ingest')
        service.post(items)

        # ingest the items and expire them
        self.ingest_items(items, provider)

        # four files in grid fs
        current_files = self.app.media.fs('upload').find()
        self.assertEqual(4, current_files.count())

        remove = RemoveExpiredContent()
        remove.run(provider.get('type'))

        # all gone
        current_files = self.app.media.fs('upload').find()
        self.assertEqual(0, current_files.count())

    def test_apply_rule_set(self):
        item = {'body_html': '@@body@@'}

        provider_name = 'reuters'
        provider = self._get_provider(provider_name)
        self.assertEqual('body', ingest.apply_rule_set(item, provider)['body_html'])

        item = {'body_html': '@@body@@'}
        provider_name = 'AAP'
        provider = self._get_provider(provider_name)
        self.assertEqual('@@body@@', ingest.apply_rule_set(item, provider)['body_html'])

    def test_all_ingested_items_have_sequence(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
        provider = self._get_provider(provider_name)
        provider_service = self._get_provider_service(provider)
        provider_service.provider = provider
        item = provider_service.fetch_ingest(guid)[0]
        get_resource_service("ingest").set_ingest_provider_sequence(item, provider)
        self.assertIsNotNone(item['ingest_provider_sequence'])

    def test_get_task_ttl(self):
        self.assertEqual(300, ingest.get_task_ttl({}))
        provider = {'update_schedule': {'minutes': 10}}
        self.assertEqual(600, ingest.get_task_ttl(provider))
        provider['update_schedule']['hours'] = 1
        provider['update_schedule']['minutes'] = 1
        self.assertEqual(3660, ingest.get_task_ttl(provider))

    def test_get_task_id(self):
        provider = {'name': 'foo', '_id': 'abc'}
        self.assertEqual('update-ingest-foo-abc', ingest.get_task_id(provider))

    def test_is_idle(self):
        provider = dict(idle_time=dict(hours=1, minutes=0))
        provider['last_item_update'] = utcnow()
        self.assertEqual(ingest.get_is_idle(provider), False)
        provider['idle_time']['hours'] = -1
        self.assertEqual(ingest.get_is_idle(provider), True)
        provider['idle_time'] = dict(hours=0, minutes=0)
        self.assertEqual(ingest.get_is_idle(provider), False)

    def test_files_dont_duplicate_ingest(self):
        provider_name = 'reuters'
        guid = 'tag_reuters.com_2014_newsml_KBN0FL0NM'
        provider = get_resource_service('ingest_providers').find_one(name=provider_name, req=None)
        provider_service = self.provider_services[provider.get('type')]
        provider_service.provider = provider

        items = provider_service.fetch_ingest(guid)
        for item in items:
            item['ingest_provider'] = provider['_id']
            item['expiry'] = utcnow() + timedelta(hours=11)

        service = get_resource_service('ingest')
        service.post(items)

        # ingest the items
        self.ingest_items(items, provider)

        items = provider_service.fetch_ingest(guid)
        for item in items:
            item['ingest_provider'] = provider['_id']
            item['expiry'] = utcnow() + timedelta(hours=11)

        # ingest them again
        self.ingest_items(items, provider)

        # 12 files in grid fs
        current_files = self.app.media.fs('upload').find()
        self.assertEqual(12, current_files.count())

    def test_anpa_category_to_subject_derived_ingest(self):
        vocab = [{'_id': 'categories', 'items': [{'is_active': True, 'name': 'Domestic Sport', 'qcode': 's',
                                                  "subject": "15000000"}]}]
        self.app.data.insert('vocabularies', vocab)

        provider_name = 'DPA'
        guid = 'IPTC7901_odd_charset.txt'
        provider = get_resource_service('ingest_providers').find_one(name=provider_name, req=None)
        provider_service = self.provider_services[provider.get('type')]
        provider_service.provider = provider

        items = provider_service.parse_file(guid, provider)
        service = get_resource_service('ingest')
        service.post(items)

        # ingest the items and check the subject code has been derived
        self.ingest_items(items, provider)
        self.assertEqual(items[0]['subject'][0]['qcode'], '15000000')

    def test_anpa_category_to_subject_derived_ingest_ignores_inactive_categories(self):
        vocab = [{'_id': 'categories', 'items': [{'is_active': False, 'name': 'Domestic Sport', 'qcode': 's',
                                                  "subject": "15000000"}]}]
        self.app.data.insert('vocabularies', vocab)

        provider_name = 'DPA'
        guid = 'IPTC7901_odd_charset.txt'
        provider = get_resource_service('ingest_providers').find_one(name=provider_name, req=None)
        provider_service = self.provider_services[provider.get('type')]
        provider_service.provider = provider

        items = provider_service.parse_file(guid, provider)
        service = get_resource_service('ingest')
        service.post(items)

        # ingest the items and check the subject code has been derived
        self.ingest_items(items, provider)
        self.assertNotIn('subject', items[0])

    def test_subject_to_anpa_category_derived_ingest(self):
        vocab = [{'_id': 'iptc_category_map',
                  'items': [{'name': 'Finance', 'category': 'f', 'subject': '04000000', 'is_active': True}]},
                 {'_id': 'categories',
                  'items': [{'is_active': True, 'name': 'Australian Weather', 'qcode': 'b', 'subject': '17000000'}]}]

        self.app.data.insert('vocabularies', vocab)

        provider_name = 'AAP'
        guid = 'nitf-fishing.xml'
        provider = get_resource_service('ingest_providers').find_one(name=provider_name, req=None)
        provider_service = self.provider_services[provider.get('type')]
        provider_service.provider = provider

        items = provider_service.parse_file(guid, provider)
        for item in items:
            item['ingest_provider'] = provider['_id']
            item['expiry'] = utcnow() + timedelta(hours=11)

        service = get_resource_service('ingest')
        service.post(items)

        # ingest the items and check the subject code has been derived
        self.ingest_items(items, provider)
        self.assertEqual(items[0]['anpa_category'][0]['qcode'], 'f')

    def test_subject_to_anpa_category_derived_ingest_ignores_inactive_map_entries(self):
        vocab = [{'_id': 'iptc_category_map',
                  'items': [{'name': 'Finance', 'category': 'f', 'subject': '04000000', 'is_active': False}]},
                 {'_id': 'categories',
                  'items': [{'is_active': True, 'name': 'Australian Weather', 'qcode': 'b', 'subject': '17000000'}]}]

        self.app.data.insert('vocabularies', vocab)

        provider_name = 'AAP'
        guid = 'nitf-fishing.xml'
        provider = get_resource_service('ingest_providers').find_one(name=provider_name, req=None)
        provider_service = self.provider_services[provider.get('type')]
        provider_service.provider = provider

        items = provider_service.parse_file(guid, provider)
        for item in items:
            item['ingest_provider'] = provider['_id']
            item['expiry'] = utcnow() + timedelta(hours=11)

        service = get_resource_service('ingest')
        service.post(items)

        # ingest the items and check the subject code has been derived
        self.ingest_items(items, provider)
        self.assertNotIn('anpa_category', items[0])
