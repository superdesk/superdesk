
import unittest
import unittest.mock
import bson
from .base_proxy import BaseProxy


class MockDatalayer():
    find_one = None
    update = None


class BaseProxyTestCase(unittest.TestCase):

    def test_update_will_use_db_id(self):
        original = {'_id': bson.ObjectId()}
        updates = {'name': 'foo', '_id': original['_id']}
        datalayer = MockDatalayer()
        datalayer.find_one = unittest.mock.MagicMock(return_value=original)
        datalayer.update = unittest.mock.MagicMock(return_value=original)
        proxy = BaseProxy(datalayer)
        proxy.update('test', {'_id': str(original['_id'])}, updates)
        datalayer.update.assert_called_with('test', original['_id'], {'name': 'foo'}, original)
