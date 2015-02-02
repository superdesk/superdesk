# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
from superdesk.errors import IngestApiError, IngestFileError, ParserError, logger
from superdesk.tests import TestCase
from nose.tools import assert_raises
from superdesk.tests import setup
import logging

class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }

class ErrorsTestCase(TestCase):
    def setUp(self):

        setup(context=self)
        test_logging = logging.getLogger('test')
        test_logging.addHandler(MockLoggingHandler())
        superdesk.logger = test_logging
        x = 5
        y = 7

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

    def test_raise_folderCreateError(self):
        with assert_raises(IngestFileError) as error_context:
            ex = Exception("Testing folderCreateError")
            raise IngestFileError.folderCreateError(ex)
        exception = error_context.exception
        self.assertTrue(exception.code == 3001)
        self.assertTrue(exception.message == "Destination folder could not be created")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing folderCreateError")

    def test_raise_fileMoveError(self):
        with assert_raises(IngestFileError) as error_context:
            ex = Exception("Testing fileMoveError")
            raise IngestFileError.fileMoveError(ex)
        exception = error_context.exception
        self.assertTrue(exception.code == 3002)
        self.assertTrue(exception.message == "Ingest file could not be copied")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing fileMoveError")


    def test_raise_parseMessageError(self):
        with assert_raises(ParserError) as error_context:
            ex = Exception("Testing parseMessageError")
            raise ParserError.parseMessageError(ex)
        exception = error_context.exception
        self.assertTrue(exception.code == 1001)
        self.assertTrue(exception.message == "Message could not be parsed")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing parseMessageError")


    def test_raise_parseFileError(self):
        with assert_raises(ParserError) as error_context:
            try:
                ex = Exception("Testing parseFileError")
                raise ex
            except Exception:
                raise ParserError.parseFileError('afp', 'test.txt', ex)
        exception = error_context.exception
        self.assertTrue(exception.code == 1002)
        self.assertTrue(exception.message == "Ingest file could not be parsed")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing parseFileError")



'''
def test_raise_anpaParseFileError(self):
        with assert_raises(ParserError) as error_context:
            ex = Exception("Testing parseFileError")
            raise ParserError.anpaParseFileError('test.txt', ex)
        exception = error_context.exception
        self.assertTrue(exception.code == 1003)
        self.assertTrue(exception.message == "ANPA file could not be parsed")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing anpaParseFileError")


    def test_raise_newsmlOneParserError(self):
        with assert_raises(ParserError) as error_context:
            ex = Exception("Testing parseFileError")
            raise ParserError.newsmlOneParserError(ex)
        exception = error_context.exception
        self.assertTrue(exception.code == 1004)
        self.assertTrue(exception.message == "NewsML1 input could not be processed")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing newsmlOneParserError")


    def test_raise_newsmlTwoParserError(self):
        with assert_raises(ParserError) as error_context:
            ex = Exception("Testing parseFileError")
            raise ParserError.newsmlTwoParserError(ex)
        exception = error_context.exception
        self.assertTrue(exception.code == 1005)
        self.assertTrue(exception.message == "NewsML2 input could not be processed")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing newsmlTwoParserError")


    def test_raise_nitfParserError(self):
        with assert_raises(ParserError) as error_context:
            ex = Exception("Testing nitfParserError")
            raise ParserError.nitfParserError(ex)
        exception = error_context.exception
        self.assertTrue(exception.code == 1006)
        self.assertTrue(exception.message == "NITF input could not be processed")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing nitfParserError")

'''
