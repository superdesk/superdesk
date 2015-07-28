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
from unittest.mock import call, MagicMock


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


class InstanceInitTestCase(RssIngestServiceTest):
    """Tests if instance is correctly initialized on creation."""

    def test_initializes_auth_info_to_none(self):
        if hasattr(self.instance, 'auth_info'):
            self.assertIsNone(self.instance.auth_info)
        else:
            self.fail('auth_info attribute not initialized')


class PrepareHrefMethodTestCase(RssIngestServiceTest):
    """Tests for the prepare_href() method."""

    def test_returns_unchanged_link_if_no_auth_info(self):
        self.instance.auth_info = None
        url = 'http://domain.com/images/foo.jpg'

        returned = self.instance.prepare_href(url)

        self.assertEqual(returned, url)

    def test_returns_link_with_auth_data_if_available(self):
        self.instance.auth_info = {
            'username': 'john doe',
            'password': 'abc+007'
        }
        url = 'http://domain.com/images/foo.jpg'

        returned = self.instance.prepare_href(url)

        self.assertEqual(
            returned, 'http://john%20doe:abc%2B007@domain.com/images/foo.jpg')


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
        self.instance._extract_image_links = MagicMock(return_value=[])
        self.instance._fetch_images = MagicMock()
        self.instance._wrap_into_package = MagicMock()

    def test_stores_auth_info_in_instance_if_auth_required(self):
        self.instance.auth_info = None
        fake_provider = {
            'config': {
                'auth_required': True,
                'username': 'james',
                'password': 'bond+007',
            }
        }

        self.instance._update(fake_provider)

        self.assertEqual(
            self.instance.auth_info,
            {'username': 'james', 'password': 'bond+007'}
        )

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

    def test_returns_items_and_package_list_if_entry_contains_image_urls(self):
        feed_parse.return_value = MagicMock(
            entries=[
                MagicMock(
                    updated_parsed=struct_time(
                        [2015, 2, 25, 17, 11, 11, 0, 0, 0])
                ),
            ]
        )

        fake_text_item = dict(
            guid='fake_text_item',
            firstcreated=datetime(2015, 2, 25, 17, 11, 11),
            versioncreated=datetime(2015, 2, 25, 17, 11, 11),
        )
        item_url = 'http://link.to/fake_item'
        fake_image_items = [
            {'guid': 'http://link.to/image_1.jpg'},
            {'guid': 'http://link.to/image_2.jpg'},
        ]
        fake_package = MagicMock(name='fake_package')

        self.instance._create_item = MagicMock(return_value=fake_text_item)
        self.instance._extract_image_links = MagicMock(return_value=[item_url])
        self.instance._create_image_items = MagicMock(
            return_value=fake_image_items)
        self.instance._create_package = MagicMock(return_value=fake_package)

        returned = self.instance._update(
            {'last_updated': datetime(1965, 2, 24)}
        )

        self.instance._create_package.assert_called_with(
            fake_text_item, fake_image_items)

        self.assertEqual(len(returned), 1)
        items = returned[0]

        expected_items = [
            fake_text_item,
            {'guid': 'http://link.to/image_1.jpg'},
            {'guid': 'http://link.to/image_2.jpg'},
            fake_package,
        ]
        self.assertCountEqual(items, expected_items)


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
                'href': 'http://foo.bar/image_1.bmp',
                'type': 'image/bmp',
            }
        ]

        links = self.instance._extract_image_links(rss_entry)

        self.assertCountEqual(links, [])

    def test_extracts_media_thumbnail_links(self):
        rss_entry = MagicMock()
        rss_entry.media_thumbnail = [
            {'url': 'http://foo.bar/small_img.gif'},
            {'url': 'http://foo.bar/thumb_x.tiff'},
        ]

        links = self.instance._extract_image_links(rss_entry)

        self.assertCountEqual(
            links,
            ['http://foo.bar/small_img.gif', 'http://foo.bar/thumb_x.tiff']
        )

    def test_omits_media_thumbnail_links_to_non_supported_formats(self):
        rss_entry = MagicMock()
        rss_entry.media_thumbnail = [
            {'url': 'http://foo.bar/image.bmp'},
        ]

        links = self.instance._extract_image_links(rss_entry)

        self.assertCountEqual(links, [])

    def test_extracts_media_content_img_links(self):
        rss_entry = MagicMock()
        rss_entry.media_content = [
            {
                'url': 'http://foo.bar/image_1.jpeg',
                'type': 'image/jpeg',
            }, {
                'url': 'http://foo.bar/image_2.tiff',
                'type': 'image/tiff',
            }
        ]

        links = self.instance._extract_image_links(rss_entry)

        self.assertCountEqual(
            links,
            ['http://foo.bar/image_1.jpeg', 'http://foo.bar/image_2.tiff']
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
                'url': 'http://foo.bar/image_1.bmp',
                'type': 'image/bmp',
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


class CreateImageItemsMethodTestCase(RssIngestServiceTest):
    """Tests for the _create_image_items() method."""

    @mock.patch('superdesk.io.rss.generate_guid')
    @mock.patch('superdesk.io.rss.GUID_TAG', 'guid_type_tag')
    def test_creates_image_items_from_given_urls(self, fake_generate_guid):
        links = [
            'http://foo.bar/image_1.jpg',
            'http://baz.ban/image_2.jpg',
        ]
        text_item = {
            'firstcreated': datetime(2015, 1, 27, 15, 56, 59),
            'versioncreated': datetime(2015, 3, 19, 17, 20, 45)
        }
        fake_generate_guid.side_effect = ('image:guid:1', 'image:guid:2')

        result = self.instance._create_image_items(links, text_item)

        self.assertEqual(
            fake_generate_guid.mock_calls,
            [call(type='guid_type_tag')] * 2
        )

        expected_result = [
            {
                'guid': 'image:guid:1',
                'type': 'picture',
                'firstcreated': datetime(2015, 1, 27, 15, 56, 59),
                'versioncreated': datetime(2015, 3, 19, 17, 20, 45),
                'renditions': {
                    'baseImage': {
                        'href': 'http://foo.bar/image_1.jpg'
                    }
                }
            }, {
                'guid': 'image:guid:2',
                'type': 'picture',
                'firstcreated': datetime(2015, 1, 27, 15, 56, 59),
                'versioncreated': datetime(2015, 3, 19, 17, 20, 45),
                'renditions': {
                    'baseImage': {
                        'href': 'http://baz.ban/image_2.jpg'
                    }
                }
            }
        ]
        self.assertCountEqual(result, expected_result)


class CreatePackageMethodTestCase(RssIngestServiceTest):
    """Tests for the _create_package() method."""

    @mock.patch('superdesk.io.rss.generate_guid')
    @mock.patch('superdesk.io.rss.GUID_TAG', 'guid_type_tag')
    def test_creates_package_from_given_text_and_image_items(
        self, fake_generate_guid
    ):
        text_item = {
            'guid': 'main_text',
            'firstcreated': datetime(2015, 1, 27, 16, 0, 0),
            'versioncreated': datetime(2015, 1, 27, 16, 0, 0),
            'headline': 'Headline of the text item'
        }
        img_item_1 = {'guid': 'image_1'}
        img_item_2 = {'guid': 'image_2'}

        fake_generate_guid.return_value = 'package:guid:abcd123'

        package = self.instance._create_package(
            text_item,
            [img_item_1, img_item_2]
        )

        fake_generate_guid.assert_called_with(type='guid_type_tag')

        expected = {
            'type': 'composite',
            'guid': 'package:guid:abcd123',
            'firstcreated': datetime(2015, 1, 27, 16, 0, 0),
            'versioncreated': datetime(2015, 1, 27, 16, 0, 0),
            'headline': 'Headline of the text item',
            'groups': [
                {
                    'id': 'root',
                    'role': 'grpRole:NEP',
                    'refs': [{'idRef': 'main'}],
                }, {
                    'id': 'main',
                    'role': 'main',
                    'refs': [
                        {'residRef': 'main_text'},
                        {'residRef': 'image_1'},
                        {'residRef': 'image_2'},
                    ],
                }
            ]
        }
        self.assertEqual(package, expected)
