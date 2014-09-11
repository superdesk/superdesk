

from superdesk.tests import TestCase
from superdesk.celery_app import loads, dumps
from bson import ObjectId
from datetime import datetime


class CeleryTestCase(TestCase):

    def test_serialize_objectid(self):
        _id = ObjectId('528de7b03b80a13eefc5e610')
        data = loads(dumps({'_id': _id}))
        self.assertEquals(data['_id'], _id)

    def test_serialize_datetime(self):
        date = datetime(2012, 12, 12, 12, 12, 12, 0)
        s = dumps({'_updated': date})
        o = loads(s)
        self.assertEquals(o['_updated'], date)
