
from superdesk.io.tests import setup_providers, teardown_providers
from superdesk.tests import setup
from unittest import TestCase
from superdesk import get_resource_service


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
            ingested_count = self.ingest_items(provider, items)
            self.assertEquals(6, ingested_count)

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
