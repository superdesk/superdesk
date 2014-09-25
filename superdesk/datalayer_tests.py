
from .tests import TestCase
import superdesk


class DatalayerTestCase(TestCase):

    def test_find_all(self):
        data = {'resource': 'test', 'action': 'get'}
        with self.app.test_request_context():
            superdesk.get_resource_service('activity').post([data])
            self.assertEquals(1, superdesk.get_resource_service('activity').get(req=None, lookup={}).count())
