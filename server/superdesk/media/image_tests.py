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
