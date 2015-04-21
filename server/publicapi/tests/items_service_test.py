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


class ItemsServiceTestCase(ApiTestCase):
    """Base class for the `items` service tests."""

    def _get_target_class(self):
        """Return the class under test.

        Make the test fail immediately if the class cannot be imported.
        """
        try:
            from publicapi.items import ItemsService
        except ImportError:
            self.fail("Could not import class under test (ItemsService).")
        else:
            return ItemsService

    def test_class_exists(self):
        self._get_target_class()  # fails if the class cannot be obtained
