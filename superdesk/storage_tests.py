
from .tests import TestCase
from .storage import FileSystemStorage


class FileSystemStorageTestCase(TestCase):

    def setUp(self):
        super(FileSystemStorageTestCase, self).setUp()
        self.storage = FileSystemStorage()
        self.storage.init_app(self.app)

    def test_put_get_file(self):
        fixture = self.get_fixture_path('flower.jpg')
        filename = 'flower.jpg'
        with open(fixture, 'rb') as f:
            filename = self.storage.save_file(filename, f)
        with self.app.test_request_context():
            resp = self.storage.send_file(filename)
        self.assertEquals(resp.status_code, 200)
