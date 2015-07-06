# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import os
from superdesk.tests import TestCase
from .image import get_meta


class ExifMetaExtractionTestCase(TestCase):

    fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
    img = os.path.join(fixtures, 'canon_exif.JPG')

    def test_extract_meta_json_serialization(self):

        with open(self.img, mode='rb') as f:
            meta = get_meta(f)

        self.assertEqual(meta['ExifImageWidth'], 32)
        self.assertEqual(meta['ExifImageHeight'], 21)
        self.assertEqual(meta['Make'], 'Canon')
        self.assertEqual(meta['Model'], 'Canon EOS 60D')


class ExifMetaWithGPSInfoExtractionTestCase(TestCase):

    fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
    img = os.path.join(fixtures, 'iphone_gpsinfo_exif.JPG')

    def test_extract_meta_json_serialization(self):
        expected_gpsinfo = {
            'GPSImgDirection': (14794, 475),
            'GPSLongitudeRef': 'W',
            'GPSImgDirectionRef': 'T',
            'GPSLongitude': ((70, 1), (38, 1), (3946, 100)),
            'GPSAltitudeRef': 0,
            'GPSLatitudeRef': 'S',
            'GPSAltitude': (105587, 183),
            'GPSLatitude': ((33, 1), (26, 1), (1150, 100)),
            'GPSTimeStamp': ((19, 1), (59, 1), (5117, 100))
        }

        with open(self.img, mode='rb') as f:
            meta = get_meta(f)

        self.assertEqual(meta.get('ExifImageWidth', None), 400)
        self.assertEqual(meta.get('ExifImageHeight', None), 300)
        self.assertEqual(meta.get('Make', None), 'Apple')
        self.assertEqual(meta.get('Model', None), 'iPhone 5')
        self.assertEqual(meta.get('GPSInfo', None), expected_gpsinfo)


class ExifMetaExtractionUserCommentRemovedTestCase(TestCase):

    fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
    # this image has UserComment exif data value as 'test'
    img = os.path.join(fixtures, 'iphone_gpsinfo_exif.JPG')

    def test_extract_meta_json_serialization(self):

        with open(self.img, mode='rb') as f:
            meta = get_meta(f)

        self.assertIsNone(meta.get('UserComment', None))
