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
from apps.archive.archive_crop import ArchiveCropService
from nose.tools import assert_raises
from superdesk.errors import SuperdeskApiError
from apps.vocabularies.command import VocabulariesPopulateCommand


class ArchiveCropTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.service = ArchiveCropService()
        with self.app.app_context():
            VocabulariesPopulateCommand().run(os.path.abspath('apps/prepopulate/data_initialization/vocabularies.json'))

    def test_validate_aspect_ratio_fails(self):
        doc = {'CropLeft': 0, 'CropRight': 80, 'CropTop': 0, 'CropBottom': 60}
        crop = {'height': 700, 'width': 70}
        with assert_raises(SuperdeskApiError):
            self.service._validate_aspect_ratio(crop, doc)

    def test_validate_aspect_ratio_fails_with_cropsize_less(self):
        doc = {'CropLeft': 0, 'CropRight': 80, 'CropTop': 0, 'CropBottom': 60}
        crop = {'height': 600, 'width': 800}
        with assert_raises(SuperdeskApiError):
            self.service._validate_aspect_ratio(crop, doc)

    def test_validate_aspect_ratio_succeeds(self):
        doc = {'CropLeft': 0, 'CropRight': 800, 'CropTop': 0, 'CropBottom': 600}
        crop = {'height': 600, 'width': 800}
        self.assertIsNone(self.service._validate_aspect_ratio(crop, doc))

    def test_validate_aspect_ratio_succeeds(self):
        doc = {'CropLeft': 0, 'CropRight': 1600, 'CropTop': 0, 'CropBottom': 1200}
        crop = {'height': 600, 'width': 800}
        self.assertIsNone(self.service._validate_aspect_ratio(crop, doc))

    def test_get_crop_by_name(self):
        with self.app.app_context():
            self.assertIsNotNone(self.service.get_crop_by_name('16-9'))
            self.assertIsNotNone(self.service.get_crop_by_name('4-3'))
            self.assertIsNone(self.service.get_crop_by_name('d'))
