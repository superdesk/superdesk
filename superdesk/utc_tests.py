
from datetime import datetime
from superdesk.tests import TestCase
from superdesk.utc import get_date


class UTCTestCase(TestCase):

    def test_get_date(self):
        self.assertIsInstance(get_date('2012-12-12'), datetime)
        self.assertIsInstance(get_date(datetime.now()), datetime)
        self.assertIsNone(get_date(None))
