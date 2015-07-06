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


class PublicApiErrorTestCase(ApiTestCase):

    def _make_one(self, *args, **kwargs):
        """Create and return a new instance of the class under test.

        Make the test fail immediately if the class cannot be imported.
        """
        try:
            from publicapi.errors import PublicApiError
        except ImportError:
            self.fail("Could not import class under test")
        else:
            return PublicApiError(*args, **kwargs)

    def test_inherits_from_superdesk_error(self):
        from superdesk.errors import SuperdeskError
        error = self._make_one()
        self.assertIsInstance(error, SuperdeskError)

    def test_uses_given_error_code(self):
        error = self._make_one(12345)
        self.assertEqual(error.status_code, 12345)

    def test_uses_default_error_code_if_error_code_not_given(self):
        error = self._make_one()
        self.assertEqual(error.status_code, 10000)

    def test_uses_default_error_message_if_error_code_not_given(self):
        error = self._make_one()
        self.assertEqual(error.message, "Unknown API error.")

    def test_uses_error_description_if_given(self):
        error = self._make_one(desc='Detailed description')
        self.assertEqual(error.payload, "Detailed description")


class UnknownParameterErrorTestCase(ApiTestCase):

    def _make_one(self, *args, **kwargs):
        """Create and return a new instance of the class under test.

        Make the test fail immediately if the class cannot be imported.
        """
        try:
            from publicapi.errors import UnexpectedParameterError
        except ImportError:
            self.fail("Could not import class under test")
        else:
            return UnexpectedParameterError(*args, **kwargs)

    def test_inherits_from_base_publicapi_error(self):
        from publicapi.errors import PublicApiError
        error = self._make_one()
        self.assertIsInstance(error, PublicApiError)

    def test_error_code(self):
        error = self._make_one()
        self.assertEqual(error.status_code, 10001)

    def test_error_message(self):
        error = self._make_one()
        self.assertEqual(error.message, "Unexpected parameter.")

    def test_uses_error_description_if_given(self):
        error = self._make_one(desc='More detailed description')
        self.assertEqual(error.payload, 'More detailed description')


class BadParameterValueTestCase(ApiTestCase):

    def _make_one(self, *args, **kwargs):
        """Create and return a new instance of the class under test.

        Make the test fail immediately if the class cannot be imported.
        """
        try:
            from publicapi.errors import BadParameterValueError
        except ImportError:
            self.fail("Could not import class under test")
        else:
            return BadParameterValueError(*args, **kwargs)

    def test_inherits_from_base_publicapi_error(self):
        from publicapi.errors import PublicApiError
        error = self._make_one()
        self.assertIsInstance(error, PublicApiError)

    def test_error_code(self):
        error = self._make_one()
        self.assertEqual(error.status_code, 10002)

    def test_error_message(self):
        error = self._make_one()
        self.assertEqual(error.message, "Bad parameter value.")

    def test_uses_error_description_if_given(self):
        error = self._make_one(desc='Integer expected for max results')
        self.assertEqual(error.payload, 'Integer expected for max results')
