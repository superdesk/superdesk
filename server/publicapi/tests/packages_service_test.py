# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from flask import Flask
from publicapi.tests import ApiTestCase
from unittest import mock


class PackagesServiceTestCase(ApiTestCase):
    """Base class for the `packages` service tests."""

    def _get_target_class(self):
        """Return the class under test.

        Make the test fail immediately if the class cannot be imported.
        """
        try:
            from publicapi.packages import PackagesService
        except ImportError:
            self.fail("Could not import class under test (PackagesService).")
        else:
            return PackagesService

    def _make_one(self, *args, **kwargs):
        """Create a new instance of the class under test."""
        return self._get_target_class()(*args, **kwargs)


@mock.patch("publicapi.packages.service.ItemsService.on_fetched_item")
class OnFetchedItemMethodTestCase(PackagesServiceTestCase):
    """Tests for the on_fetched_item() method."""

    def setUp(self):
        super().setUp()

        self.app = Flask(__name__)
        self.app.config['PUBLICAPI_URL'] = 'http://api.com'
        self.app.config['URLS'] = {
            'items': 'items_endpoint',
            'packages': 'packages_endpoint'
        }

        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()
        super().tearDown()

    def test_invokes_superclass_method_with_correct_args(self, super_fetched):
        document = {'_id': 'item:XYZ'}
        instance = self._make_one(datasource='packages')
        instance.on_fetched_item(document)
        super_fetched.assert_called_with(document)

    def test_sets_uri_field_on_referenced_items(self, super_fetched):
        document = {
            '_id': 'item:XYZ',
            'associations': {
                'main_picture': {'type': 'picture', '_id': 'img:123'},
            }
        }

        instance = self._make_one(datasource='packages')
        instance.on_fetched_item(document)

        expected_assoc = {
            'main_picture': {
                'type': 'picture',
                'uri': 'http://api.com/items_endpoint/img%3A123'
            }
        }
        self.assertEqual(document.get('associations'), expected_assoc)

    def test_sets_uri_field_on_referenced_packages(self, super_fetched):
        document = {
            '_id': 'item:XYZ',
            'associations': {
                'story_object': {'type': 'composite', '_id': 'pkg:456'}
            }
        }

        instance = self._make_one(datasource='packages')
        instance.on_fetched_item(document)

        expected_assoc = {
            'story_object': {
                'type': 'composite',
                'uri': 'http://api.com/packages_endpoint/pkg%3A456'
            }
        }
        self.assertEqual(document.get('associations'), expected_assoc)


@mock.patch("publicapi.packages.service.ItemsService.on_fetched")
class OnFetchedMethodTestCase(PackagesServiceTestCase):
    """Tests for the on_fetched() method."""

    def setUp(self):
        super().setUp()

        self.app = Flask(__name__)
        self.app.config['PUBLICAPI_URL'] = 'http://api.com'
        self.app.config['URLS'] = {
            'items': 'items_endpoint',
            'packages': 'packages_endpoint'
        }

        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()
        super().tearDown()

    def test_invokes_superclass_method_with_correct_args(self, super_fetched):
        result = {
            '_items': []
        }
        instance = self._make_one(datasource='packages')
        instance.on_fetched(result)
        super_fetched.assert_called_with(result)

    def test_sets_uri_field_on_objects_referenced_by_fetched_packages(
        self, super_fetched
    ):
        result = {
            '_items': [
                {
                    '_id': 'pkg:ABC',
                    'associations': {
                        'main_picture': {'type': 'picture', '_id': 'img:123'},
                    }
                },
                {
                    '_id': 'pkg:DEF',
                    'associations': {
                        'main_story': {'type': 'composite', '_id': 'pkg:456'},
                    }
                },
            ]
        }

        instance = self._make_one(datasource='packages')
        instance.on_fetched(result)

        # check 1st fetched package's associations
        expected_assoc = {
            'main_picture': {
                'type': 'picture',
                'uri': 'http://api.com/items_endpoint/img%3A123'
            }
        }
        fetched_package = result['_items'][0]
        self.assertEqual(fetched_package.get('associations'), expected_assoc)

        # check 2nd fetched package's associations
        expected_assoc = {
            'main_story': {
                'type': 'composite',
                'uri': 'http://api.com/packages_endpoint/pkg%3A456'
            }
        }
        fetched_package = result['_items'][1]
        self.assertEqual(fetched_package.get('associations'), expected_assoc)
