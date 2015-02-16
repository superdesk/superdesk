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


class FakeIngestError(Exception):
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
@mock.patch('superdesk.io.rss.ProviderError.ingestError', FakeIngestError)
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

    def test_raises_ingest_error_on_network_error(self):
        self.instance._fetch_data.side_effect = Exception("Timeout!")
        try:
            with self.assertRaises(FakeIngestError):
                self.instance._update({})
        except:
            self.fail('Invalid exception type raised.')

    def test_raises_ingest_error_on_parse_error(self):
        feed_parse.side_effect = Exception("Parse error!")
        try:
            with self.assertRaises(FakeIngestError):
                self.instance._update({})
        except:
            self.fail('Invalid exception type raised.')

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

        self.assertEquals(len(returned), 1)
        items = returned[0]
        self.assertEquals(items, [item_1, item_2])

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

        self.assertEquals(len(returned), 1)
        items = returned[0]
        self.assertEquals(len(items), 0)


@mock.patch('superdesk.io.rss.requests.get', requests_get)
class FetchDataMethodTestCase(RssIngestServiceTest):
    """Tests for the _fetch_data() method."""

    def setUp(self):
        super(FetchDataMethodTestCase, self).setUp()
        requests_get.reset_mock()

    def test_retrieves_feed_from_correct_url(self):
        requests_get.return_value = MagicMock(ok=True)
        config = dict(url='http://news.com/rss')

        self.instance._fetch_data(config)

        call_args = requests_get.call_args[0]
        self.assertEquals(call_args[0], 'http://news.com/rss')

    def test_provides_auth_info_if_available(self):
        requests_get.return_value = MagicMock(ok=True)
        config = dict(
            url='http://news.com/rss',
            username='johndoe',
            password='secret')

        self.instance._fetch_data(config)

        kw_call_args = requests_get.call_args[1]
        self.assertEquals(kw_call_args.get('auth'), ('johndoe', 'secret'))

    def test_returns_fetched_data_on_success(self):
        requests_get.return_value = MagicMock(ok=True, content='<rss>X</rss>')
        config = dict(url='http://news.com/rss')

        response = self.instance._fetch_data(config)

        self.assertEquals(response, '<rss>X</rss>')

    def test_raises_error_on_error_response(self):
        requests_get.return_value = MagicMock(ok=False)
        config = dict(url='http://news.com/rss')

        with self.assertRaises(Exception):
            self.instance._fetch_data(config)


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

        self.assertEquals(item['guid'], 'http://news.com/rss/1234abcd')
        self.assertEquals(item['uri'], 'http://news.com/rss/1234abcd')
        self.assertEquals(
            item['firstcreated'], datetime(2015, 2, 25, 16, 45, 23))
        self.assertEquals(
            item['versioncreated'], datetime(2015, 2, 25, 17, 52, 11))
        self.assertEquals(item['headline'], 'Breaking News!')
        self.assertEquals(item['abstract'], 'Something happened...')
        self.assertEquals(item['body_text'], 'This is body text.')
