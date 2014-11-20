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
