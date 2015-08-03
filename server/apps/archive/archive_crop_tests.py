# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.tests import TestCase
from apps.archive.archive_crop import ArchiveCropService
from nose.tools import assert_raises
from superdesk.errors import SuperdeskApiError


class ArchiveCropTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.service = ArchiveCropService()

    def test_validate_aspect_ratio_fails(self):
        doc = {'CropLeft': 0, 'CropRight': 80, 'CropTop': 0, 'CropBottom': 60}
        crop = {'height': 700, 'width': 70}
        with assert_raises(SuperdeskApiError):
            self.service._validate_aspect_ratio(crop, doc)

    def test_validate_aspect_ratio_succeeds(self):
        doc = {'CropLeft': 0, 'CropRight': 80, 'CropTop': 0, 'CropBottom': 60}
        crop = {'height': 300, 'width': 400}
        self.assertIsNone(self.service._validate_aspect_ratio(crop, doc))

    def test_get_crop_by_name(self):
        crops = [{'name': 'acrop'}, {'name': '4-9'}, {'name': 'Second'}, {'name': 'c'}]
        self.assertIsNotNone(self.service._get_crop_by_name(crops, 'second'))
        self.assertIsNotNone(self.service._get_crop_by_name(crops, '4-9'))
        self.assertIsNone(self.service._get_crop_by_name(crops, 'd'))
        self.assertIsNotNone(self.service._get_crop_by_name(crops, 'ACROP'))
