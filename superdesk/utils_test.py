
from superdesk.tests import TestCase
from .utils import last_updated
from .utc import utcnow


class UtilsTestCase(TestCase):

    def test_last_updated(self):
        with self.app.app_context():
            self.assertEquals('2012', last_updated(
                {self.app.config['LAST_UPDATED']: '2011'},
                {self.app.config['LAST_UPDATED']: '2012'},
                {self.app.config['LAST_UPDATED']: '2010'},
                {},
                None
            ))

            now = utcnow()
            self.assertGreaterEqual(last_updated(), now)
