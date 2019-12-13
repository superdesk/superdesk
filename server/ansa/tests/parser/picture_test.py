
import os

from superdesk.tests import TestCase
from unittest.mock import MagicMock, patch
from ansa.parser.picture import PictureParser
from ansa.subjects import init_app as init_subjects
from ansa.constants import PHOTO_CATEGORIES_ID, PRODUCTS_ID
from datetime import datetime
from pytz import utc


class PictureParserTestCase(TestCase):

    def setUp(self):
        super().setUp()
        init_subjects(self.app)

        self.app.media = MagicMock()

        self.app.config.update({
            'SERVER_DOMAIN': 'test',
            'RENDITIONS': {'picture': {}},
        })

        self.app.data.insert('vocabularies', [
            {'_id': PHOTO_CATEGORIES_ID, 'items': [
                {'name': 'FOO', 'qcode': 'foo', 'is_active': True},
                {'name': 'SPO', 'qcode': 'spo', 'is_active': True},
            ]},
            {'_id': PRODUCTS_ID, 'items': [
                {'name': 'Foo', 'qcode': 'FOO', 'is_active': True},
                {'name': 'Photo', 'qcode': 'PHOTO', 'is_active': True},
            ]},
        ])

    @patch('superdesk.io.feed_parsers.image_iptc.get_renditions_spec', return_value={})
    @patch('superdesk.io.feed_parsers.image_iptc.generate_renditions', return_value={})
    def test_parse_picture(self, get_renditions_spec, generate_renditions):
        parser = PictureParser()
        path = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'iptc.jpg')
        item = parser.parse_item(path)

        # use filename as id
        self.assertEqual('iptc.jpg', item['uri'])
        self.assertEqual('iptc.jpg', item['guid'])

        # core metadata
        self.assertEqual('UAE FORMULA ONE GRAND PRIX 2018', item['slugline'])
        self.assertEqual('SRDJAN SUKI', item['byline'])
        self.assertEqual('Formula One Grand Prix of Abu Dhabi', item['headline'])
        self.assertEqual('EPA', item['copyrightholder'])
        self.assertEqual('ANSA', item['copyrightnotice'])
        self.assertEqual('ANSA', item['usageterms'])
        self.assertEqual('en', item['language'])

        self.assertIn({
            'name': 'Sport',
            'qcode': '15000000',
            'parent': None,
        }, item['subject'])

        self.assertIn({
            'name': 'SPO',
            'qcode': 'spo',
            'scheme': PHOTO_CATEGORIES_ID,
        }, item['subject'])

        self.assertIn({
            'name': 'Photo',
            'qcode': 'PHOTO',
            'scheme': PRODUCTS_ID,
        }, item['subject'])

        # extra metadata
        self.assertEqual('ABU DHABI', item['extra']['city'])
        self.assertEqual('UNITED ARAB EMIRATES', item['extra']['nation'])
        self.assertEqual('ss MR', item['extra']['digitator'])
        self.assertEqual('STF', item['extra']['coauthor'])
        self.assertEqual('ANSA', item['extra']['supplier'])
        self.assertEqual('2019-11-29T14:05:31+04:00', item['extra']['DateCreated'].isoformat())
        self.assertEqual('2019-11-29T16:41:44+01:00', item['extra']['DateRelease'].isoformat())

    def test_parse_datetime(self):
        parser = PictureParser()
        date = datetime(2019, 12, 13, 13, 32, 5, tzinfo=utc)

        self.assertEqual(date, parser.parse_date_time('20191213', '133205+0000'))
        self.assertEqual(date, parser.parse_date_time('2019-12-13', '13:32:05+0000'))

        # default rome is +1
        self.assertEqual(date, parser.parse_date_time('20191213', '143205'))
        self.assertEqual(date, parser.parse_date_time('2019-12-13', '14:32:05'))
