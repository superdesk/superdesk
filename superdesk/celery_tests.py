

from superdesk.tests import TestCase
from superdesk.celery_app import try_cast, loads
from bson import ObjectId
from datetime import datetime
from eve.utils import date_to_str


class CeleryTestCase(TestCase):

    _id = ObjectId('528de7b03b80a13eefc5e610')

    def test_cast_objectid(self):
        self.assertEquals(try_cast(str(self._id)), self._id)

    def test_cast_datetime(self):
        date = datetime(2012, 12, 12, 12, 12, 12, 0)
        with self.app.app_context():
            s = date_to_str(date)
            self.assertEquals(try_cast(s).day, date.day)

    def test_loads_args(self):
        s = b'{"args": [{"_id": "528de7b03b80a13eefc5e610", "_updated": "2014-09-10T14:31:09+0000"}]}'
        o = loads(s)
        self.assertEquals(o['args'][0]['_id'], self._id)
        self.assertIsInstance(o['args'][0]['_updated'], datetime)
