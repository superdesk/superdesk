from superdesk.tests import TestCase
from superdesk import get_backend
from superdesk.utc import utcnow
from datetime import timedelta


class BackendTestCase(TestCase):

    def test_update_change_etag(self):
        backend = get_backend()
        updates = {'name': 'foo'}
        item = {'name': 'bar'}
        with self.app.app_context():
            ids = backend.create('ingest', [item])
            doc_old = backend.find_one('ingest', None, _id=ids[0])
            backend.update('ingest', ids[0], updates)
            doc_new = backend.find_one('ingest', None, _id=ids[0])
            self.assertNotEqual(doc_old[self.app.config['ETAG']],
                                doc_new[self.app.config['ETAG']])

    def test_check_default_dates_on_create(self):
        backend = get_backend()
        item = {'name': 'foo'}
        with self.app.app_context():
            ids = backend.create('ingest', [item])
            doc = backend.find_one('ingest', None, _id=ids[0])
            self.assertIn(self.app.config['DATE_CREATED'], doc)
            self.assertIn(self.app.config['LAST_UPDATED'], doc)

    def test_check_default_dates_on_create(self):
        backend = get_backend()
        past = (utcnow() + timedelta(seconds=-2)).replace(microsecond=0)
        item = {'name': 'foo',
                self.app.config['DATE_CREATED']: past,
                self.app.config['LAST_UPDATED']: past}
        updates = {'name': 'bar'}
        with self.app.app_context():
            ids = backend.create('ingest', [item])
            doc_old = backend.find_one('ingest', None, _id=ids[0])
            backend.update('ingest', ids[0], updates)
            doc_new = backend.find_one('ingest', None, _id=ids[0])
            date1 = doc_old[self.app.config['LAST_UPDATED']]
            date2 = doc_new[self.app.config['LAST_UPDATED']]
            self.assertGreaterEqual(date2, date1)
            date1 = doc_old[self.app.config['DATE_CREATED']]
            date2 = doc_new[self.app.config['DATE_CREATED']]
            self.assertEqual(date1, date2)
