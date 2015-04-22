# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from publicapi.tests import ApiTestCase

from unittest import mock
from unittest.mock import MagicMock


_fake_items_resource = MagicMock()
_fake_items_service = MagicMock()
_fake_backend = MagicMock(name='superdesk backend')


def _fake_get_backend():
    """Return mocked superdesk backend."""
    return _fake_backend


class FakeItemsService():
    def __init__(self, endpoint_name, backend=None):
        self.endpoint_name = endpoint_name
        self.backend = backend

    def __eq__(self, other):
        return (
            self.endpoint_name == other.endpoint_name and
            self.backend is other.backend
        )

    def __ne__(self, other):
        return not self.__eq__(other)


@mock.patch('publicapi.items.ItemsResource', _fake_items_resource)
@mock.patch('publicapi.items.ItemsService', FakeItemsService)
@mock.patch('superdesk.get_backend', _fake_get_backend)
class ItemsInitAppTestCase(ApiTestCase):
    """Base class for the `items.init_app` function tests."""

    def _get_target_function(self):
        """Return the function under test.

        Make the test fail immediately if the function cannot be imported.
        """
        try:
            from publicapi.items import init_app
        except ImportError:
            self.fail("Could not import function under test (init_app).")
        else:
            return init_app

    def test_instantiates_items_resource_with_correct_arguments(self):
        fake_app = MagicMock(name='app')
        fake_items_service = FakeItemsService('items', _fake_get_backend())

        init_app = self._get_target_function()
        init_app(fake_app)

        self.assertTrue(_fake_items_resource.called)
        args, kwargs = _fake_items_resource.call_args

        self.assertTrue(len(args) > 0 and args[0] == 'items')
        self.assertIs(kwargs.get('app'), fake_app)
        self.assertEqual(kwargs.get('service'), fake_items_service)
