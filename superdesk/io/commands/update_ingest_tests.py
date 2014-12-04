
from unittest import TestCase
from datetime import timedelta
from superdesk import get_resource_service
from superdesk.utc import utcnow
from superdesk.tests import setup
from superdesk.io import register_provider
from superdesk.io.tests import setup_providers, teardown_providers
from superdesk.io.ingest_service import IngestService
from superdesk.io.commands.update_ingest import is_scheduled, update_provider
from superdesk.io.ingest_service import IngestProviderClosedError


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

    def test_ingest_items(self):
        provider_name = 'reuters'
        guid = 'tag:reuters.com,2014:newsml_KBN0FL0NM'
        with self.app.app_context():
            provider = get_resource_service('ingest_providers').find_one(name=provider_name, req=None)
            provider_service = self.provider_services[provider.get('type')]
            provider_service.provider = provider
            items = provider_service.fetch_ingest(guid)
            items.extend(provider_service.fetch_ingest(guid))
            self.assertEquals(12, len(items))
            self.ingest_items(provider, items)

    def test_ingest_item_sync_if_missing_from_elastic(self):
        provider_name = 'reuters'
        guid = 'tag:reuters.com,2014:newsml_KBN0FL0NM'
        with self.app.app_context():
            provider = get_resource_service('ingest_providers').find_one(name=provider_name, req=None)
            provider_service = self.provider_services[provider.get('type')]
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

        aap = self.provider_services[provider.get('type')]
        self.assertRaises(IngestProviderClosedError, aap.update, provider)

    def test_is_scheduled(self):
        self.assertTrue(is_scheduled({}), 'for first time it should run')
        self.assertFalse(is_scheduled({'last_updated': utcnow()}), 'then it should wait default time 5m')
        self.assertTrue(is_scheduled({'last_updated': utcnow() - timedelta(minutes=6)}), 'after 5m it should run again')
        self.assertFalse(is_scheduled({
            'last_updated': utcnow() - timedelta(minutes=6),
            'update_schedule': {'minutes': 10}
        }), 'or wait if provider has specific schedule')
        self.assertTrue(is_scheduled({
            'last_updated': utcnow() - timedelta(minutes=11),
            'update_schedule': {'minutes': 10}
        }), 'and run eventually')

    def test_change_last_updated(self):
        with self.app.app_context():
            ids = self.app.data.insert('ingest_providers', [{'type': 'test', '_etag': 'test'}])
            update_provider(str(ids[0]))
            provider = self.app.data.find_one('ingest_providers', req=None, _id=ids[0])
            self.assertGreaterEqual(utcnow(), provider.get('last_updated'))
            self.assertEqual('test', provider.get('_etag'))
