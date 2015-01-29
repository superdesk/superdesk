# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.errors import IngestApiError
from superdesk.tests import TestCase
from nose.tools import assert_raises


class ErrorsTestCase(TestCase):

    def test_raise_apiRequestError(self):
        with assert_raises(IngestApiError) as error_context:
            ex = Exception("Testing apiRequestError")
            raise IngestApiError.apiRequestError(ex)
        exception = error_context.exception
        self.assertTrue(exception.code == 4003)
        self.assertTrue(exception.message == "API ingest has request error")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing apiRequestError")

    def test_raise_apiTimeoutError(self):
        with assert_raises(IngestApiError) as error_context:
            ex = Exception("Testing apiTimeoutError")
            raise IngestApiError.apiTimeoutError(ex)
        exception = error_context.exception
        self.assertTrue(exception.code == 4001)
        self.assertTrue(exception.message == "API ingest connection has timed out.")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing apiTimeoutError")

    def test_raise_apiRedirectError(self):
        with assert_raises(IngestApiError) as error_context:
            ex = Exception("Testing apiRedirectError")
            raise IngestApiError.apiRedirectError(ex)
        exception = error_context.exception
        self.assertTrue(exception.code == 4002)
        self.assertTrue(exception.message == "API ingest has too many redirects")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing apiRedirectError")

    def test_raise_apiUnicodeError(self):
        with assert_raises(IngestApiError) as error_context:
            ex = Exception("Testing apiUnicodeError")
            raise IngestApiError.apiUnicodeError(ex)
        exception = error_context.exception
        self.assertTrue(exception.code == 4004)
        self.assertTrue(exception.message == "API ingest Unicode Encode Error")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing apiUnicodeError")

    def test_raise_apiParseError(self):
        with assert_raises(IngestApiError) as error_context:
            ex = Exception("Testing apiParseError")
            raise IngestApiError.apiParseError(ex)
        exception = error_context.exception
        self.assertTrue(exception.code == 4005)
        self.assertTrue(exception.message == "API ingest xml parse error")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing apiParseError")
