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
from requests.exceptions import RequestException
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

    @classmethod
    def apiRequestError(cls, exception, provider):
        return RssError('request_error', exception, provider)


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
        super().setUp()
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
        super().setUp()
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


class ExtractImageLinksMethodTestCase(RssIngestServiceTest):
    """Tests for the _extract_image_links() method."""

    def test_extracts_enclosure_img_links(self):
        rss_entry = MagicMock()
        rss_entry.links = [
            {
                'rel': 'enclosure',
                'href': 'http://foo.bar/image_1.jpg',
                'type': 'image/jpeg',
            }, {
                'rel': 'enclosure',
                'href': 'http://foo.bar/image_2.png',
                'type': 'image/png',
            }
        ]

        links = self.instance._extract_image_links(rss_entry)

        self.assertCountEqual(
            links,
            ['http://foo.bar/image_1.jpg', 'http://foo.bar/image_2.png']
        )

    def test_omits_enclosure_links_to_non_supported_mime_types(self):
        rss_entry = MagicMock()
        rss_entry.links = [
            {
                'rel': 'alternative',
                'href': 'http://foo.bar/81fecd',
                'type': 'text/html',
            }, {
                'rel': 'enclosure',
                'href': 'http://foo.bar/image_1.tiff',
                'type': 'image/tiff',
            }
        ]

        links = self.instance._extract_image_links(rss_entry)

        self.assertCountEqual(links, [])

    def test_extracts_media_thumbnail_links(self):
        rss_entry = MagicMock()
        rss_entry.media_thumbnail = [
            {'url': 'http://foo.bar/small_img.jpg'},
            {'url': 'http://foo.bar/thumb_x.png'},
        ]

        links = self.instance._extract_image_links(rss_entry)

        self.assertCountEqual(
            links,
            ['http://foo.bar/small_img.jpg', 'http://foo.bar/thumb_x.png']
        )

    def test_omits_media_thumbnail_links_to_non_supported_formats(self):
        rss_entry = MagicMock()
        rss_entry.media_thumbnail = [
            {'url': 'http://foo.bar/image.tiff'},
        ]

        links = self.instance._extract_image_links(rss_entry)

        self.assertCountEqual(links, [])

    def test_extracts_media_content_img_links(self):
        rss_entry = MagicMock()
        rss_entry.media_content = [
            {
                'url': 'http://foo.bar/image_1.jpg',
                'type': 'image/jpeg',
            }, {
                'url': 'http://foo.bar/image_2.png',
                'type': 'image/png',
            }
        ]

        links = self.instance._extract_image_links(rss_entry)

        self.assertCountEqual(
            links,
            ['http://foo.bar/image_1.jpg', 'http://foo.bar/image_2.png']
        )

    def test_omits_media_content_links_to_non_supported_mime_types(self):
        rss_entry = MagicMock()
        rss_entry.media_content = [
            {
                'url': 'http://foo.bar/music.mp3',
                'type': 'audio/mpeg3',
            }, {
                'url': 'http://foo.bar/video.avi',
                'type': 'video/avi',
            }, {
                'url': 'http://foo.bar/image_1.tiff',
                'type': 'image/tiff',
            }
        ]

        links = self.instance._extract_image_links(rss_entry)

        self.assertCountEqual(links, [])

    def test_omits_duplicate_links(self):
        rss_entry = MagicMock()
        rss_entry.links = [
            {
                'rel': 'enclosure',
                'href': 'http://foo.bar/image.png',
                'type': 'image/png',
            }, {
                'rel': 'enclosure',
                'href': 'http://foo.bar/image.png',
                'type': 'image/png',
            }
        ]
        rss_entry.media_content = [
            {
                'url': 'http://foo.bar/image.png',
                'type': 'image/png',
            }, {
                'url': 'http://foo.bar/image.png',
                'type': 'image/jpeg',
            }
        ]

        links = self.instance._extract_image_links(rss_entry)

        self.assertCountEqual(links, ['http://foo.bar/image.png'])


@mock.patch('superdesk.io.rss.IngestApiError', FakeIngestApiError)
class FetchImagesMethodTestCase(RssIngestServiceTest):
    """Tests for the _fetch_images() method."""

    def setUp(self):
        super().setUp()
        self.fake_provider = MagicMock(name='fake provider')

    @mock.patch('superdesk.io.rss.requests.get')
    def test_fetches_images_from_all_given_urls(self, requests_get):
        url_1 = 'http://foo.bar/image_1.jpg'
        url_2 = 'http://foo.bar/image_2.jpg'
        links = [url_1, url_2]

        response_1 = MagicMock(name='response_1')
        response_1.ok = True
        response_1.url = url_1
        response_1.content = b'img_1 data'

        response_2 = MagicMock(name='response_2')
        response_2.ok = True
        response_2.url = url_2
        response_2.content = b'img_2 data'

        wrong_response = MagicMock(name='wrong_response')
        wrong_response.ok = True
        wrong_response.url = 'http://should.not/be/called'
        wrong_response.content = b'wrong image'

        def side_effect(url, *args, **kwargs):
            response = {url_1: response_1, url_2: response_2}
            return response.get(url, wrong_response)

        requests_get.side_effect = side_effect

        result = self.instance._fetch_images(links, self.fake_provider)

        expected_result = {
            url_1: b'img_1 data',
            url_2: b'img_2 data'
        }
        self.assertEqual(result, expected_result)

    @mock.patch('superdesk.io.rss.requests.get')
    def test_raises_error_on_request_error(self, requests_get):
        requests_get.side_effect = RequestException
        links = ['http://imagine.this/timeouts']

        try:
            with self.assertRaises(RssError) as exc_context:
                self.instance._fetch_images(links, self.fake_provider)
        except AssertionError:
            raise
        except:
            self.fail('Unexpected exception type raised.')

        ex = exc_context.exception
        self.assertEqual(ex.name, 'request_error')
        self.assertIs(ex.provider, self.fake_provider)

    @mock.patch('superdesk.io.rss.requests.get')
    def test_raises_error_on_non_ok_response(self, requests_get):
        response = MagicMock()
        response.ok = False

        requests_get.return_value = response
        links = ['http://imagine.this/is/not/found']

        try:
            with self.assertRaises(RssError) as exc_context:
                self.instance._fetch_images(links, self.fake_provider)
        except AssertionError:
            raise
        except:
            self.fail('Unexpected exception type raised.')

        ex = exc_context.exception
        self.assertEqual(ex.name, 'request_error')
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
        self.assertEqual(item.get('body_html'), 'This is body text.')

    def test_creates_item_taking_field_name_aliases_into_account(self):
        data = dict(
            guid='http://news.com/rss/1234abcd',
            published_parsed=struct_time([2015, 2, 25, 16, 45, 23, 2, 56, 0]),
            updated_parsed=struct_time([2015, 2, 25, 17, 52, 11, 2, 56, 0]),
            title_field_alias='Breaking News!',
            summary_field_alias='Something happened...',
            body_text_field_alias='This is body text.',
        )

        field_aliases = [{'title': 'title_field_alias'},
                         {'summary': 'summary_field_alias'},
                         {'body_text': 'body_text_field_alias'}]

        item = self.instance._create_item(data, field_aliases)

        self.assertEqual(item.get('guid'), 'http://news.com/rss/1234abcd')
        self.assertEqual(item.get('uri'), 'http://news.com/rss/1234abcd')
        self.assertEqual(item.get('type'), 'text')
        self.assertEqual(
            item.get('firstcreated'), datetime(2015, 2, 25, 16, 45, 23))
        self.assertEqual(
            item.get('versioncreated'), datetime(2015, 2, 25, 17, 52, 11))
        self.assertEqual(item.get('headline'), 'Breaking News!')
        self.assertEqual(item.get('abstract'), 'Something happened...')
        self.assertEqual(item.get('body_html'), 'This is body text.')
