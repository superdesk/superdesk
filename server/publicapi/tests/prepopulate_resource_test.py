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


class PrepopulateResourceTestCase(ApiTestCase):
    """Tests for the `prepopulate` resource."""

    def _get_target_class(self):
        """Return the class under test.

        Make the test fail immediately if the class cannot be imported.
        """
        try:
            from publicapi.prepopulate import PrepopulateResource
        except ImportError:
            self.fail("Could not import class under test (PrepopulateResource).")
        else:
            return PrepopulateResource

    def test_allowed_resource_http_methods(self):
        klass = self._get_target_class()
        self.assertEqual(klass.resource_methods, ['POST'])
