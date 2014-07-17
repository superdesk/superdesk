
import os
from superdesk.tests import TestCase
from .image import get_meta


class ExifMetaExtractionTestCase(TestCase):

    fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
    img = os.path.join(fixtures, 'canon_exif.JPG')

    def test_extract_meta_json_serialization(self):

        with open(self.img, mode='rb') as f:
            meta = get_meta(f)

        self.assertEquals(meta['ExifImageWidth'], 32)
        self.assertEquals(meta['ExifImageHeight'], 21)
        self.assertEquals(meta['Make'], 'Canon')
        self.assertEquals(meta['Model'], 'Canon EOS 60D')
