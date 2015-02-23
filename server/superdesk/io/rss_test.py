# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from datetime import datetime
from superdesk.tests import TestCase
from time import struct_time
from unittest import mock
from unittest.mock import MagicMock


feed_parse = MagicMock()
requests_get = MagicMock()


class RssError(Exception):
    def __init__(self, name, orig_ex, provider):
        self.name = name
        self.orig_ex = orig_ex
        self.provider = provider


class FakeIngestApiError(Exception):
    """Mocked factory for ingest API errors."""

    @classmethod
    def apiGeneralError(cls, exception, provider):
        return RssError('general_error', exception, provider)

    @classmethod
    def apiNotFoundError(cls, exception, provider):
        return RssError('not_found_error', exception, provider)

    @classmethod
    def apiAuthError(cls, exception, provider):
        return RssError('auth_error', exception, provider)


class FakeParseError(Exception):
    pass


class RssIngestServiceTest(TestCase):
    """Base class for RssIngestService tests."""

    def setUp(self):
        try:
            from superdesk.io.rss import RssIngestService
        except ImportError:
            # a missing class should result in a test failure, not in an error
            self.fail("Could not import class under test (RssIngestService).")
        else:
            self.instance = RssIngestService()


@mock.patch('superdesk.io.rss.feedparser.parse', feed_parse)
@mock.patch('superdesk.io.rss.IngestApiError', FakeIngestApiError)
@mock.patch('superdesk.io.rss.ParserError.parseMessageError', FakeParseError)
class UpdateMethodTestCase(RssIngestServiceTest):
    """Tests for the _update() method."""

    def _hard_reset_mock(self, mock):
        """Reset a mock and also clear its return value and side effects.

        :param MagicMock mock: mock instance to reset
        """
        mock.reset_mock()
        mock.return_value = MagicMock(name='mock()')
        mock.side_effect = None

    def setUp(self):
        super(UpdateMethodTestCase, self).setUp()
        self._hard_reset_mock(feed_parse)
        self.instance._fetch_data = MagicMock(return_value='<rss>foo</rss>')
        self.instance._create_item = MagicMock(return_value={})

    def test_raises_ingest_error_if_fetching_data_fails(self):
        self.instance._fetch_data.side_effect = FakeIngestApiError
        try:
            with self.assertRaises(FakeIngestApiError):
                self.instance._update({})
        except:
            self.fail('Expected exception type was not raised.')

    def test_raises_ingest_error_on_parse_error(self):
        feed_parse.side_effect = Exception("Parse error!")
        try:
            with self.assertRaises(FakeParseError):
                self.instance._update({})
        except:
            self.fail('Expected exception type was not raised.')

    def test_returns_items_built_from_retrieved_data(self):
        feed_parse.return_value = MagicMock(
            entries=[
                MagicMock(
                    updated_parsed=struct_time(
                        [2015, 2, 25, 17, 11, 11, 2, 56, 0])
                ),
                MagicMock(
                    updated_parsed=struct_time(
                        [2015, 2, 25, 17, 22, 22, 2, 56, 0])
                ),
            ]
        )

        item_1 = dict(
            guid='item_1',
            firstcreated=datetime(2015, 2, 25, 17, 11, 11),
            versioncreated=datetime(2015, 2, 25, 17, 11, 11),
        )
        item_2 = dict(
            guid='item_2',
            firstcreated=datetime(2015, 2, 25, 17, 22, 22),
            versioncreated=datetime(2015, 2, 25, 17, 22, 22),
        )
        self.instance._create_item.side_effect = [item_1, item_2]

        returned = self.instance._update(
            {'last_updated': datetime(2015, 2, 25, 14, 0, 0)}
        )

        self.assertEqual(len(returned), 1)
        items = returned[0]
        self.assertEqual(items, [item_1, item_2])

    def test_does_not_return_old_items(self):
        feed_parse.return_value = MagicMock(
            entries=[
                MagicMock(
                    updated_parsed=struct_time(
                        [2015, 2, 25, 11, 11, 11, 2, 56, 0])
                ),
            ]
        )

        item = dict(
            guid='item_1',
            firstcreated=datetime(2015, 2, 25, 11, 11, 11),
            versioncreated=datetime(2015, 2, 25, 11, 11, 11),
        )
        self.instance._create_item.return_value = item

        returned = self.instance._update(
            {'last_updated': datetime(2015, 2, 25, 15, 0, 0)}
        )

        self.assertEqual(len(returned), 1)
        items = returned[0]
        self.assertEqual(len(items), 0)


@mock.patch('superdesk.io.rss.requests.get', requests_get)
@mock.patch('superdesk.io.rss.IngestApiError', FakeIngestApiError)
class FetchDataMethodTestCase(RssIngestServiceTest):
    """Tests for the _fetch_data() method."""

    def setUp(self):
        super(FetchDataMethodTestCase, self).setUp()
        requests_get.reset_mock()
        self.fake_provider = MagicMock(name='fake provider')

    def test_retrieves_feed_from_correct_url(self):
        requests_get.return_value = MagicMock(ok=True)
        config = dict(url='http://news.com/rss')

        self.instance._fetch_data(config, self.fake_provider)

        call_args = requests_get.call_args[0]
        self.assertEqual(call_args[0], 'http://news.com/rss')

    def test_provides_auth_info_if_required(self):
        requests_get.return_value = MagicMock(ok=True)
        config = dict(
            url='http://news.com/rss',
            auth_required=True,
            username='johndoe',
            password='secret')

        self.instance._fetch_data(config, self.fake_provider)

        kw_call_args = requests_get.call_args[1]
        self.assertEqual(kw_call_args.get('auth'), ('johndoe', 'secret'))

    def test_returns_fetched_data_on_success(self):
        requests_get.return_value = MagicMock(ok=True, content='<rss>X</rss>')
        config = dict(url='http://news.com/rss')

        response = self.instance._fetch_data(config, self.fake_provider)

        self.assertEqual(response, '<rss>X</rss>')

    def test_raises_auth_error_on_401(self):
        requests_get.return_value = MagicMock(
            ok=False, status_code=401, reason='invalid credentials')
        config = dict(url='http://news.com/rss')

        try:
            with self.assertRaises(RssError) as exc_context:
                self.instance._fetch_data(config, self.fake_provider)
        except:
            self.fail('Expected exception type was not raised.')

        ex = exc_context.exception
        self.assertEqual(ex.name, 'auth_error')
        self.assertEqual(ex.orig_ex.args[0], 'invalid credentials')
        self.assertIs(ex.provider, self.fake_provider)

    def test_raises_auth_error_on_403(self):
        requests_get.return_value = MagicMock(
            ok=False, status_code=403, reason='access forbidden')
        config = dict(url='http://news.com/rss')

        try:
            with self.assertRaises(RssError) as exc_context:
                self.instance._fetch_data(config, self.fake_provider)
        except:
            self.fail('Expected exception type was not raised.')

        ex = exc_context.exception
        self.assertEqual(ex.name, 'auth_error')
        self.assertEqual(ex.orig_ex.args[0], 'access forbidden')
        self.assertIs(ex.provider, self.fake_provider)

    def test_raises_not_found_error_on_404(self):
        requests_get.return_value = MagicMock(
            ok=False, status_code=404, reason='resource not found')
        config = dict(url='http://news.com/rss')

        try:
            with self.assertRaises(RssError) as exc_context:
                self.instance._fetch_data(config, self.fake_provider)
        except:
            self.fail('Expected exception type was not raised.')

        ex = exc_context.exception
        self.assertEqual(ex.name, 'not_found_error')
        self.assertEqual(ex.orig_ex.args[0], 'resource not found')
        self.assertIs(ex.provider, self.fake_provider)

    def test_raises_general_error_on_unknown_error(self):
        requests_get.return_value = MagicMock(
            ok=False, status_code=500, reason='server down')
        config = dict(url='http://news.com/rss')

        try:
            with self.assertRaises(RssError) as exc_context:
                self.instance._fetch_data(config, self.fake_provider)
        except:
            self.fail('Expected exception type was not raised.')

        ex = exc_context.exception
        self.assertEqual(ex.name, 'general_error')
        self.assertEqual(ex.orig_ex.args[0], 'server down')
        self.assertIs(ex.provider, self.fake_provider)


class CreateItemMethodTestCase(RssIngestServiceTest):
    """Tests for the _create_item() method."""

    def test_creates_item_from_given_data(self):
        data = dict(
            guid='http://news.com/rss/1234abcd',
            published_parsed=struct_time([2015, 2, 25, 16, 45, 23, 2, 56, 0]),
            updated_parsed=struct_time([2015, 2, 25, 17, 52, 11, 2, 56, 0]),
            title='Breaking News!',
            summary='Something happened...',
            body_text='This is body text.',
        )

        item = self.instance._create_item(data)

        self.assertEqual(item.get('guid'), 'http://news.com/rss/1234abcd')
        self.assertEqual(item.get('uri'), 'http://news.com/rss/1234abcd')
        self.assertEqual(item.get('type'), 'text')
        self.assertEqual(
            item.get('firstcreated'), datetime(2015, 2, 25, 16, 45, 23))
        self.assertEqual(
            item.get('versioncreated'), datetime(2015, 2, 25, 17, 52, 11))
        self.assertEqual(item.get('headline'), 'Breaking News!')
        self.assertEqual(item.get('abstract'), 'Something happened...')
        self.assertEqual(item.get('body_text'), 'This is body text.')
