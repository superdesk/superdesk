
from .tests import TestCase
import superdesk
from settings import URL_PREFIX


class DatalayerTestCase(TestCase):

    def test_find_all(self):
        data = {'resource': 'test', 'action': 'get'}
        with self.app.test_request_context(URL_PREFIX):
            superdesk.get_resource_service('activity').post([data])
            self.assertEquals(1, superdesk.get_resource_service('activity').get(req=None, lookup={}).count())
