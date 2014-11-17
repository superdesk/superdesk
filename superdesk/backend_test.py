
from superdesk.tests import TestCase
from superdesk import get_backend


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
