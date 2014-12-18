
import os
import glob
import shutil
import tempfile
import unittest

from superdesk.utc import utcnow
from .ftp import FTPService


PREFIX = 'test_superdesk_'


class FTPTestCase(unittest.TestCase):

    def test_it_can_connect(self):
        service = FTPService()

        if 'FTP_URL' not in os.environ:
            return

        config = service.configFromURL(os.environ['FTP_URL'])
        self.assertEqual('test', config['path'])
        self.assertEqual('localhost', config['host'])

        config['dest_path'] = tempfile.mkdtemp(prefix=PREFIX)
        provider = {'config': config}

        items = service._update(provider)
        self.assertEqual(266, len(items))

        provider['last_updated'] = utcnow()
        self.assertEqual(0, len(service._update(provider)))

        self.assertTrue(os.path.isdir(provider['config']['dest_path']))
        self.assertEqual(266, len(os.listdir(provider['config']['dest_path'])))

    def tearDown(self):
        for folder in glob.glob('/tmp/%s*' % (PREFIX)):
            shutil.rmtree(folder)
