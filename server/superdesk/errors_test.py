# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk import errors
from superdesk.errors import IngestApiError, IngestFileError, \
    ParserError, ProviderError, IngestFtpError
from superdesk.tests import TestCase, setup_notification
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

    mock_logger_handler = {}

    def setUp(self):
        setup(context=self)
        setup_notification(context=self)
        mock_logger = logging.getLogger('test')
        self.mock_logger_handler = MockLoggingHandler()
        mock_logger.addHandler(self.mock_logger_handler)
        errors.logger = mock_logger
        errors.notifiers = []
        self.provider = {'name': 'TestProvider'}

    def test_raise_apiRequestError(self):
        with assert_raises(IngestApiError) as error_context:
            ex = Exception("Testing apiRequestError")
            raise IngestApiError.apiRequestError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 4003)
        self.assertTrue(exception.message == "API ingest has request error")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing apiRequestError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "IngestApiError Error 4003 - API ingest has request error: "
                         "Testing apiRequestError on channel TestProvider")

    def test_raise_apiTimeoutError(self):
        with assert_raises(IngestApiError) as error_context:
            ex = Exception("Testing apiTimeoutError")
            raise IngestApiError.apiTimeoutError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 4001)
        self.assertTrue(exception.message == "API ingest connection has timed out.")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing apiTimeoutError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "IngestApiError Error 4001 - API ingest connection has timed out.: "
                         "Testing apiTimeoutError on channel TestProvider")

    def test_raise_apiRedirectError(self):
        with assert_raises(IngestApiError) as error_context:
            ex = Exception("Testing apiRedirectError")
            raise IngestApiError.apiRedirectError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 4002)
        self.assertTrue(exception.message == "API ingest has too many redirects")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing apiRedirectError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "IngestApiError Error 4002 - API ingest has too many redirects: "
                         "Testing apiRedirectError on channel TestProvider")

    def test_raise_apiUnicodeError(self):
        with assert_raises(IngestApiError) as error_context:
            ex = Exception("Testing apiUnicodeError")
            raise IngestApiError.apiUnicodeError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 4004)
        self.assertTrue(exception.message == "API ingest Unicode Encode Error")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing apiUnicodeError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "IngestApiError Error 4004 - API ingest Unicode Encode Error: "
                         "Testing apiUnicodeError on channel TestProvider")

    def test_raise_apiParseError(self):
        with assert_raises(IngestApiError) as error_context:
            ex = Exception("Testing apiParseError")
            raise IngestApiError.apiParseError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 4005)
        self.assertTrue(exception.message == "API ingest xml parse error")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing apiParseError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "IngestApiError Error 4005 - API ingest xml parse error: "
                         "Testing apiParseError on channel TestProvider")

    def test_raise_apiNotFoundError(self):
        with assert_raises(IngestApiError) as error_context:
            ex = Exception("Testing apiNotFoundError")
            raise IngestApiError.apiNotFoundError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 4006)
        self.assertTrue(exception.message == "API service not found(404) error")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing apiNotFoundError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "IngestApiError Error 4006 - API service not found(404) error: "
                         "Testing apiNotFoundError on channel TestProvider")

    def test_raise_folderCreateError(self):
        with assert_raises(IngestFileError) as error_context:
            ex = Exception("Testing folderCreateError")
            raise IngestFileError.folderCreateError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 3001)
        self.assertTrue(exception.message == "Destination folder could not be created")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing folderCreateError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "IngestFileError Error 3001 - Destination folder could not be created: "
                         "Testing folderCreateError on channel TestProvider")

    def test_raise_fileMoveError(self):
        with assert_raises(IngestFileError) as error_context:
            ex = Exception("Testing fileMoveError")
            raise IngestFileError.fileMoveError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 3002)
        self.assertTrue(exception.message == "Ingest file could not be copied")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing fileMoveError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "IngestFileError Error 3002 - Ingest file could not be copied: "
                         "Testing fileMoveError on channel TestProvider")

    def test_raise_parseMessageError(self):
        with assert_raises(ParserError) as error_context:
            ex = Exception("Testing parseMessageError")
            raise ParserError.parseMessageError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 1001)
        self.assertTrue(exception.message == "Message could not be parsed")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing parseMessageError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "ParserError Error 1001 - Message could not be parsed: "
                         "Testing parseMessageError on channel TestProvider")

    def test_raise_parseFileError(self):
        with assert_raises(ParserError) as error_context:
            try:
                ex = Exception("Testing parseFileError")
                raise ex
            except Exception:
                raise ParserError.parseFileError('afp', 'test.txt', ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 1002)
        self.assertTrue(exception.message == "Ingest file could not be parsed")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing parseFileError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 2)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "Source Type: afp - File: test.txt could not be processed")
        self.assertEqual(self.mock_logger_handler.messages['error'][1],
                         "ParserError Error 1002 - Ingest file could not be parsed: "
                         "Testing parseFileError on channel TestProvider")

    def test_raise_newsmlOneParserError(self):
        with assert_raises(ParserError) as error_context:
            try:
                ex = Exception("Testing newsmlOneParserError")
                raise ex
            except Exception:
                raise ParserError.newsmlOneParserError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 1004)
        self.assertTrue(exception.message == "NewsML1 input could not be processed")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing newsmlOneParserError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "ParserError Error 1004 - NewsML1 input could not be processed: "
                         "Testing newsmlOneParserError on channel TestProvider")

    def test_raise_newsmlTwoParserError(self):
        with assert_raises(ParserError) as error_context:
            try:
                ex = Exception("Testing newsmlTwoParserError")
                raise ex
            except Exception:
                raise ParserError.newsmlTwoParserError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 1005)
        self.assertTrue(exception.message == "NewsML2 input could not be processed")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing newsmlTwoParserError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "ParserError Error 1005 - NewsML2 input could not be processed: "
                         "Testing newsmlTwoParserError on channel TestProvider")

    def test_raise_nitfParserError(self):
        with assert_raises(ParserError) as error_context:
            try:
                ex = Exception("Testing nitfParserError")
                raise ex
            except Exception:
                raise ParserError.nitfParserError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 1006)
        self.assertTrue(exception.message == "NITF input could not be processed")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing nitfParserError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "ParserError Error 1006 - NITF input could not be processed: "
                         "Testing nitfParserError on channel TestProvider")

    def test_raise_folderCreateError(self):
        with assert_raises(IngestFileError) as error_context:
            try:
                ex = Exception("Testing folderCreateError")
                raise ex
            except Exception:
                raise IngestFileError.folderCreateError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 3001)
        self.assertTrue(exception.message == "Destination folder could not be created")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing folderCreateError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "IngestFileError Error 3001 - Destination folder could not be created: "
                         "Testing folderCreateError on channel TestProvider")

    def test_raise_fileMoveError(self):
        with assert_raises(IngestFileError) as error_context:
            try:
                ex = Exception("Testing fileMoveError")
                raise ex
            except Exception:
                raise IngestFileError.fileMoveError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 3002)
        self.assertTrue(exception.message == "Ingest file could not be copied")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing fileMoveError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "IngestFileError Error 3002 - Ingest file could not be copied: "
                         "Testing fileMoveError on channel TestProvider")

    def test_raise_providerAddError(self):
        with assert_raises(ProviderError) as error_context:
            try:
                ex = Exception("Testing providerAddError")
                raise ex
            except Exception:
                raise ProviderError.providerAddError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 2001)
        self.assertTrue(exception.message == "Provider could not be saved")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing providerAddError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "ProviderError Error 2001 - Provider could not be saved: "
                         "Testing providerAddError on channel TestProvider")

    def test_raise_expiredContentError(self):
        with assert_raises(ProviderError) as error_context:
            try:
                ex = Exception("Testing expiredContentError")
                raise ex
            except Exception:
                raise ProviderError.expiredContentError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 2002)
        self.assertTrue(exception.message == "Expired content could not be removed")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing expiredContentError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "ProviderError Error 2002 - Expired content could not be removed: "
                         "Testing expiredContentError on channel TestProvider")

    def test_raise_ruleError(self):
        with assert_raises(ProviderError) as error_context:
            try:
                ex = Exception("Testing ruleError")
                raise ex
            except Exception:
                raise ProviderError.ruleError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 2003)
        self.assertTrue(exception.message == "Rule could not be applied")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing ruleError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "ProviderError Error 2003 - Rule could not be applied: "
                         "Testing ruleError on channel TestProvider")

    def test_raise_ingestError(self):
        with assert_raises(ProviderError) as error_context:
            try:
                ex = Exception("Testing ingestError")
                raise ex
            except Exception:
                raise ProviderError.ingestError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 2004)
        self.assertTrue(exception.message == "Ingest error")
        self.assertTrue(exception.provider_name == "TestProvider")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing ingestError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "ProviderError Error 2004 - Ingest error: "
                         "Testing ingestError on channel TestProvider")

    def test_raise_anpaError(self):
        with assert_raises(ProviderError) as error_context:
            try:
                ex = Exception("Testing anpaError")
                raise ex
            except Exception:
                raise ProviderError.anpaError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 2005)
        self.assertTrue(exception.message == "Anpa category error")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing anpaError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "ProviderError Error 2005 - Anpa category error: "
                         "Testing anpaError on channel TestProvider")

    def test_raise_providerFilterExpiredContentError(self):
        with assert_raises(ProviderError) as error_context:
            try:
                ex = Exception("Testing providerFilterExpiredContentError")
                raise ex
            except Exception:
                raise ProviderError.providerFilterExpiredContentError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 2006)
        self.assertTrue(exception.message == "Expired content could not be filtered")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing providerFilterExpiredContentError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "ProviderError Error 2006 - Expired content could not be filtered: "
                         "Testing providerFilterExpiredContentError on channel TestProvider")

    def test_raise_ftpError(self):
        with assert_raises(IngestFtpError) as error_context:
            try:
                ex = Exception("Testing ftpError")
                raise ex
            except Exception:
                raise IngestFtpError.ftpError(ex, self.provider)
        exception = error_context.exception
        self.assertTrue(exception.code == 5000)
        self.assertTrue(exception.message == "FTP ingest error")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing ftpError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "IngestFtpError Error 5000 - FTP ingest error: "
                         "Testing ftpError on channel TestProvider")

    def test_raise_ftpUnknownParserError(self):
        with assert_raises(IngestFtpError) as error_context:
            try:
                ex = Exception("Testing ftpUnknownParserError")
                raise ex
            except Exception:
                raise IngestFtpError.ftpUnknownParserError(ex, self.provider, 'test.xml')
        exception = error_context.exception
        self.assertTrue(exception.code == 5001)
        self.assertTrue(exception.message == "FTP parser could not be found")
        self.assertIsNotNone(exception.system_exception)
        self.assertEquals(exception.system_exception.args[0], "Testing ftpUnknownParserError")
        self.assertEqual(len(self.mock_logger_handler.messages['error']), 2)
        self.assertEqual(self.mock_logger_handler.messages['error'][1],
                         "IngestFtpError Error 5001 - FTP parser could not be found: "
                         "Testing ftpUnknownParserError on channel TestProvider")
        self.assertEqual(self.mock_logger_handler.messages['error'][0],
                         "Provider: TestProvider - File: test.xml unknown file format. "
                         "Parser couldn't be found.")


class RssIngestErrorsTestCase(ErrorsTestCase):
    """Tests for the IngestRssFeedError class."""

    def _get_target_class(self):
        """Return a class under test.

        If the class cannot be imported, make the test fail immediately.
        """
        try:
            from superdesk.errors import IngestRssFeedError
        except ImportError:
            self.fail(
                "Could not import class under test (IngestRssFeedError).")
        else:
            return IngestRssFeedError

    def setUp(self):
        super(RssIngestErrorsTestCase, self).setUp()
        self.exc_class = self._get_target_class()

    def test_raise_rss_ingest_general_error(self):
        with assert_raises(self.exc_class) as error_context:
            ex = Exception("Testing RSS general error")
            raise self.exc_class.generalError(ex, self.provider)

        exception = error_context.exception
        self.assertEqual(exception.code, 6000)
        self.assertEqual(exception.message, "General RSS feed error")
        self.assertEqual(exception.provider_name, "TestProvider")

        self.assertIsNotNone(exception.system_exception)
        self.assertEqual(
            exception.system_exception.args[0], "Testing RSS general error")

        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(
            self.mock_logger_handler.messages['error'][0],
            "IngestRssFeedError Error 6000 - General RSS feed error: "
            "Testing RSS general error on channel TestProvider")

    def test_raise_rss_timeout_error(self):
        with assert_raises(self.exc_class) as error_context:
            ex = Exception("Testing RSS timeout error")
            raise self.exc_class.timeoutError(ex, self.provider)

        exception = error_context.exception
        self.assertEqual(exception.code, 6001)
        self.assertEqual(
            exception.message, "RSS feed connection has timed out")
        self.assertEqual(exception.provider_name, "TestProvider")

        self.assertIsNotNone(exception.system_exception)
        self.assertEqual(
            exception.system_exception.args[0], "Testing RSS timeout error")

        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(
            self.mock_logger_handler.messages['error'][0],
            "IngestRssFeedError Error 6001 - "
            "RSS feed connection has timed out: "
            "Testing RSS timeout error on channel TestProvider")

    def test_raise_rss_not_found_error(self):
        with assert_raises(self.exc_class) as error_context:
            ex = Exception("Testing RSS not found error")
            raise self.exc_class.notFoundError(ex, self.provider)

        exception = error_context.exception
        self.assertEqual(exception.code, 6002)
        self.assertEqual(
            exception.message, "RSS feed not found (404)")
        self.assertEqual(exception.provider_name, "TestProvider")

        self.assertIsNotNone(exception.system_exception)
        self.assertEqual(
            exception.system_exception.args[0], "Testing RSS not found error")

        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(
            self.mock_logger_handler.messages['error'][0],
            "IngestRssFeedError Error 6002 - RSS feed not found (404): "
            "Testing RSS not found error on channel TestProvider")

    def test_raise_rss_authorization_error(self):
        with assert_raises(self.exc_class) as error_context:
            ex = Exception("Testing RSS authorization error")
            raise self.exc_class.authError(ex, self.provider)

        exception = error_context.exception
        self.assertEqual(exception.code, 6003)
        self.assertEqual(
            exception.message, "RSS feed authorization error")
        self.assertEqual(exception.provider_name, "TestProvider")

        self.assertIsNotNone(exception.system_exception)
        self.assertEqual(
            exception.system_exception.args[0],
            "Testing RSS authorization error")

        self.assertEqual(len(self.mock_logger_handler.messages['error']), 1)
        self.assertEqual(
            self.mock_logger_handler.messages['error'][0],
            "IngestRssFeedError Error 6003 - RSS feed authorization error: "
            "Testing RSS authorization error on channel TestProvider")
