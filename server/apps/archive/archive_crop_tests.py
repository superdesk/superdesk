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
from test_factory import SuperdeskTestCase
from unittest import mock
from apps.archive.archive_crop import ArchiveCropService
from nose.tools import assert_raises
from superdesk.errors import SuperdeskApiError
from apps.vocabularies.command import VocabulariesPopulateCommand


class ArchiveCropTestCase(SuperdeskTestCase):

    def setUp(self):
        super().setUp()
        self.service = ArchiveCropService()
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
        self.assertIsNotNone(self.service.get_crop_by_name('16-9'))
        self.assertIsNotNone(self.service.get_crop_by_name('4-3'))
        self.assertIsNone(self.service.get_crop_by_name('d'))

    def test_validate_crop_raises_error_if_item_is_not_picture(self):
        original = {"type": "text"}
        doc = {'CropLeft': 0, 'CropRight': 800, 'CropTop': 0, 'CropBottom': 600}
        with self.assertRaises(SuperdeskApiError) as context:
            self.service.validate_crop(original, "4-3", doc)

        ex = context.exception
        self.assertEqual(ex.message, 'Only images can be cropped!')
        self.assertEqual(ex.status_code, 400)

    def test_validate_crop_raises_error_if_renditions_are_missing(self):
        original = {"type": "picture"}
        doc = {'CropLeft': 0, 'CropRight': 800, 'CropTop': 0, 'CropBottom': 600}
        with self.assertRaises(SuperdeskApiError) as context:
            self.service.validate_crop(original, "4-3", doc)

        ex = context.exception
        self.assertEqual(ex.message, 'Missing renditions!')
        self.assertEqual(ex.status_code, 400)

    def test_validate_crop_raises_error_if_original_rendition_is_missing(self):
        original = {"type": "picture",
                    "renditions": {"4-3": {'CropLeft': 0, 'CropRight': 800, 'CropTop': 0, 'CropBottom': 600}}}
        doc = {'CropLeft': 0, 'CropRight': 800, 'CropTop': 0, 'CropBottom': 600}
        with self.assertRaises(SuperdeskApiError) as context:
            self.service.validate_crop(original, "4-3", doc)

        ex = context.exception
        self.assertEqual(ex.message, 'Missing original rendition!')
        self.assertEqual(ex.status_code, 400)

    def test_validate_crop_raises_error_if_crop_name_is_unknown(self):
        original = {"type": "picture",
                    "renditions": {
                        "original": {'CropLeft': 0, 'CropRight': 800, 'CropTop': 0, 'CropBottom': 600}
                    }
                    }
        doc = {'CropLeft': 0, 'CropRight': 800, 'CropTop': 0, 'CropBottom': 600}
        with self.assertRaises(SuperdeskApiError) as context:
            self.service.validate_crop(original, "d", doc)

        ex = context.exception
        self.assertEqual(ex.message, 'Unknown crop name!')
        self.assertEqual(ex.status_code, 400)

    def test_add_crop_raises_error_if_original_missing(self):
        original = {
            'renditions': {
                '4-3': {
                }
            }
        }
        doc = {'CropLeft': 0, 'CropRight': 800, 'CropTop': 0, 'CropBottom': 600}
        with self.assertRaises(SuperdeskApiError) as context:
            self.service.create_crop(original, '4-3', doc)

        ex = context.exception
        self.assertEqual(ex.message, 'Original file couldn\'t be found')
        self.assertEqual(ex.status_code, 400)

    @mock.patch('apps.archive.archive_crop.crop_image', return_value=(False, 'test'))
    def test_add_crop_raises_error(self, crop_name):
        original = {
            'renditions': {
                'original': {
                }
            }
        }

        media = mock.MagicMock()
        media.name = 'test.jpg'

        with mock.patch('superdesk.app.media.get', return_value=media):
            doc = {'CropLeft': 0, 'CropRight': 800, 'CropTop': 0, 'CropBottom': 600}
            with self.assertRaises(SuperdeskApiError) as context:
                self.service.create_crop(original, '4-3', doc)

            ex = context.exception
            self.assertEqual(ex.message, 'Saving crop failed: test')
            self.assertEqual(ex.status_code, 400)
