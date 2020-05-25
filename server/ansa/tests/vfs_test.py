
import io
import flask
import logging
import unittest
import ansa.vfs as vfs
import requests_mock

UPLOAD_URL = 'http://vfs/bdmvfs/rest/uploadfile'
UPLOAD_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<files>
  <fileItems>
    <md5>acbd18db4cc2f85cedef654fccc4a4d8</md5>
    <fsize>3</fsize>
    <mimetype>text/plain</mimetype>
    <filename>foo.txt</filename>
    <created>2015-11-05T00:00:00+01:00</created>
  </fileItems>
</files>
"""
BINARY_URL = 'http://vfs/bdmvfs/rest/binfilebymd5/foo'
METADATA_URL = 'http://vfs/bdmvfs/rest/infofilebymd5/foo'
METADATA_RESPONSE = UPLOAD_RESPONSE
NOT_FOUND_RESPONSE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<files>
    <errors>
        <code>4</code>
        <message>Error code 4 : File not found</message>
    </errors>
</files>
"""
DELETE_URL = 'http://vfs/bdmvfs/rest/deletefilebymd5/foo'
PUT_METADATA_URL = 'http://vfs/bdmvfs/rest/uploadfilemeta'
PUT_METADATA_RESPONSE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<files>
    <fileItems>
        <md5>bar</md5>
    </fileItems>
</files>
"""
DELETE_MISSING_FILE_RESPONSE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<files>
    <errors>
        <code>1</code>
        <message>Error code 1 : Application error</message>
        <specific>DaoException: File to delete not found, md5 = 84804ef7279886c76b9712687e41e0fb</specific>
    </errors>
</files>
"""


def download_url(x):
    return x


class VFSTestCase(unittest.TestCase):

    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.config['ANSA_VFS'] = 'http://vfs/'
        self.app.download_url = download_url
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.media = vfs.VFSMediaStorage(self.app)

    def tearDown(self):
        self.ctx.pop()

    def test_put(self):
        data = io.BytesIO(b'foo')
        with requests_mock.mock() as mock:
            mock.post(UPLOAD_URL, content=UPLOAD_RESPONSE.encode('utf-8'))
            _id = self.media.put(data, 'foo', 'text/plain', {}, folder='x')
            self.assertEqual('acbd18db4cc2f85cedef654fccc4a4d8', _id)

            with self.assertRaises(vfs.VFSError) as err:
                data = io.BytesIO(b'bar')
                self.media.put(data, 'foo', 'text/plain', {}, folder='x')
                self.assertIn('filename=foo', err.msg)
                self.assertIn('size=3', err.msg)
                tmpfile = err.msg.split('tmpfile=')[1].split(' ')[0]
                with open(tmpfile) as tmp:
                    self.assertEqual(data.read(), tmp.read())

    def test_get_binary(self):
        with requests_mock.mock() as mock:
            mock.get(BINARY_URL, content=b'foo')
            mock.get(METADATA_URL, content=METADATA_RESPONSE.encode('utf-8'))
            media = self.media.get('foo')
            self.assertIsNotNone(media)
            self.assertEqual('foo', media._id)
            self.assertEqual('acbd18db4cc2f85cedef654fccc4a4d8', media.md5)
            self.assertEqual(b'foo', media.read())
            self.assertEqual('text/plain', media.content_type)
            self.assertEqual(3, media.length)
            self.assertEqual('foo.txt', media.name)
            self.assertEqual('foo.txt', media.filename)
            self.assertEqual('2015-11-05T00:00:00+01:00', media.upload_date.isoformat())

    def test_exists(self):
        with requests_mock.mock() as mock:
            mock.get(METADATA_URL, content=METADATA_RESPONSE.encode('utf-8'))
            mock.get(METADATA_URL.replace('foo', 'bar'), content=NOT_FOUND_RESPONSE.encode('utf-8'))
            self.assertTrue(self.media.exists('foo'))
            self.assertFalse(self.media.exists('bar'))

    def test_delete(self):
        with requests_mock.mock() as mock:
            mock.delete(DELETE_URL, content=METADATA_RESPONSE.encode('utf-8'))
            self.media.delete('foo')

    def test_delete_graceful(self):
        with requests_mock.mock() as mock:
            mock.delete(DELETE_URL, content=DELETE_MISSING_FILE_RESPONSE.encode('utf-8'))
            with self.assertLogs(level=logging.WARNING) as log:
                self.media.delete('foo')
                self.assertEqual(1, len(log.output))
                self.assertIn('File was removed already from vfs md5=foo', log.output[0])

    def test_url_for_media(self):
        self.assertEqual(BINARY_URL, self.media.url_for_media('foo', 'image/jpeg'))

    def test_url_for_download(self):
        self.assertEqual('foo', self.media.url_for_download('foo', 'text/plain'))

    def test_get_filename(self):
        with requests_mock.mock() as mock:
            mock.get(METADATA_URL, content=METADATA_RESPONSE.encode('utf-8'))
            self.assertEqual('foo.txt', self.media.getFilename('foo'))

    def test_remove_unreferenced_files(self):
        self.media.remove_unreferenced_files([], 'upload')

    def test_fetch_rendition(self):
        with requests_mock.mock() as mock:
            mock.get(BINARY_URL, content=b'foo')
            mock.get(METADATA_URL, content=METADATA_RESPONSE.encode('utf-8'))
            media = self.media.fetch_rendition({'media': 'foo'})
            self.assertEqual(b'foo', media.read())

    def test_put_metadata(self):
        with requests_mock.mock() as mock:
            mock.post(PUT_METADATA_URL, content=PUT_METADATA_RESPONSE.encode('utf-8'))
            md5 = self.media.put_metadata('foo', {})
            self.assertEqual('bar', md5)
