
from .tests import TestCase


class DatalayerTestCase(TestCase):

    def test_find_all(self):
        data = {'resource': 'test', 'action': 'get'}
        with self.app.test_request_context():
            self.app.data.insert('activity', [data])
            self.assertEquals(1, self.app.data.find_all('activity').count())
