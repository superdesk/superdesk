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

        self.assertEquals(meta['ExifImageWidth'], 32)
        self.assertEquals(meta['ExifImageHeight'], 21)
        self.assertEquals(meta['Make'], 'Canon')
        self.assertEquals(meta['Model'], 'Canon EOS 60D')

class ExifMetaWithGPSInfoExtractionTestCase(TestCase):

    fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures')
    img = os.path.join(fixtures, 'iphone_gpsinfo_exif.JPG')
    expected_gpsinfo = {'GPSImgDirection': (14794, 475), 'GPSLongitudeRef': 'W', 'GPSImgDirectionRef': 'T', 'GPSLongitude': ((70, 1), (38, 1), (3946, 100)), 'GPSAltitudeRef': 0, 'GPSLatitudeRef': 'S', 'GPSAltitude': (105587, 183), 'GPSLatitude': ((33, 1), (26, 1), (1150, 100)), 'GPSTimeStamp': ((19, 1), (59, 1), (5117, 100))}

    def test_extract_meta_json_serialization(self):

        with open(self.img, mode='rb') as f:
            meta = get_meta(f)

        self.assertEquals(meta['ExifImageWidth'], 3264)
        self.assertEquals(meta['ExifImageHeight'], 2448)
        self.assertEquals(meta['Make'], 'Apple')
        self.assertEquals(meta['Model'], 'iPhone 5')
        self.assertEquals(meta['GPSInfo'], self.expected_gpsinfo)
