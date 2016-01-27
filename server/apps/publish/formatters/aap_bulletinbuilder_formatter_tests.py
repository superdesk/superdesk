# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.publish.subscribers import SUBSCRIBER_TYPES
from eve.utils import config
from test_factory import SuperdeskTestCase
from apps.publish import init_app
from apps.publish.formatters.aap_bulletinbuilder_formatter import AAPBulletinBuilderFormatter
from superdesk.utils import json_serialize_datetime_objectId
from superdesk import json
from superdesk.metadata.item import ITEM_TYPE, PACKAGE_TYPE
from superdesk.utc import utcnow
from bson import ObjectId


class AapBulletinBuilderFormatterTest(SuperdeskTestCase):
    subscribers = [{"_id": "1", "name": "Test", "subscriber_type": SUBSCRIBER_TYPES.WIRE, "media_type": "media",
                    "is_active": True, "sequence_num_settings": {"max": 10, "min": 1},
                    "destinations": [{"name": "AAP Bulletin Builder", "delivery_type": "pull",
                                      "format": "AAP BULLETIN BUILDER"
                                      }]
                    }]

    def setUp(self):
        super().setUp()
        self.app.data.insert('subscribers', self.subscribers)
        init_app(self.app)
        self._formatter = AAPBulletinBuilderFormatter()

    def test_bulletin_builder_formatter(self):
        article = {
            config.ID_FIELD: '123',
            config.VERSION: 2,
            'source': 'AAP',
            'anpa_category': [{'qcode': 'a'}],
            'headline': 'This is a test headline',
            'byline': 'joe',
            'slugline': 'slugline',
            'subject': [{'qcode': '02011001'}],
            'anpa_take_key': 'take_key',
            'unique_id': '1',
            'type': 'preformatted',
            'body_html': 'The story body',
            'word_count': '1',
            'priority': '1',
            'firstcreated': utcnow(),
            'versioncreated': utcnow(),
            'lock_user': ObjectId()
        }

        subscriber = self.app.data.find('subscribers', None, None)[0]
        seq, item = self._formatter.format(article, subscriber)[0]
        self.assertGreater(int(seq), 0)
        self.assertEqual(article[config.ID_FIELD], item.get('id'))
        self.assertEqual(article[config.VERSION], item.get('version'))
        self.assertEqual(article[ITEM_TYPE], item.get(ITEM_TYPE))
        self.assertEqual(article.get(PACKAGE_TYPE, ''), item.get(PACKAGE_TYPE))
        self.assertEqual(article['headline'], item.get('headline'))
        self.assertEqual(article['slugline'], item.get('slugline'))
        self.assertEqual(json.dumps(article, default=json_serialize_datetime_objectId),
                         item.get('data'))

    def test_strip_html(self):
        article = {
            config.ID_FIELD: '123',
            config.VERSION: 2,
            'source': 'AAP',
            'headline': 'This is a test headline',
            'type': 'text',
            'body_html': ('<p>The story body line 1<br>Line 2</p>'
                          '<p>abcdefghi abcdefghi abcdefghi abcdefghi abcdefghi'
                          '<span> abcdefghi</span> abcdefghi abcdefghi more</p>'
                          '<table><tr><td>test</td></tr></table>')
        }

        body_text = ('The story body line 1 Line 2\r\n\r\n'
                     'abcdefghi abcdefghi abcdefghi abcdefghi abcdefghi'
                     ' abcdefghi abcdefghi abcdefghi more\r\n\r\n'
                     'test')

        subscriber = self.app.data.find('subscribers', None, None)[0]
        seq, item = self._formatter.format(article, subscriber)[0]
        self.assertGreater(int(seq), 0)
        test_article = json.loads(item.get('data'))
        self.assertEqual(test_article['body_text'], body_text)

    def test_strip_html_case1(self):
        article = {
            config.ID_FIELD: '123',
            config.VERSION: 2,
            'source': 'AAP',
            'headline': 'This is a test headline',
            'type': 'text',
            'body_html': ('<p>The story body line 1<br>Line 2</p>'
                          '<p>abcdefghi abcdefghi abcdefghi abcdefghi abcdefghi'
                          '<span> abcdefghi</span> abcdefghi abcdefghi more</p>'
                          '<table><tr><td>test</td></tr></table>')
        }

        body_text = ('The story body line 1 Line 2\r\n\r\n'
                     'abcdefghi abcdefghi abcdefghi abcdefghi abcdefghi'
                     ' abcdefghi abcdefghi abcdefghi more\r\n\r\n'
                     'test')

        subscriber = self.app.data.find('subscribers', None, None)[0]
        seq, item = self._formatter.format(article, subscriber)[0]
        self.assertGreater(int(seq), 0)
        test_article = json.loads(item.get('data'))
        self.assertEqual(test_article['body_text'], body_text)

    def test_strip_html_case2(self):
        article = {
            config.ID_FIELD: '123',
            config.VERSION: 2,
            'source': 'AAP',
            'headline': 'This is a test headline',
            'type': 'text',
            'body_html': ('<p>This is third<br> take.</p><br><p>Correction in the third take.</p><br>'
                          '<p>This is test.</p><br><p><br></p>')
        }

        body_text = ('This is third take.\r\n\r\n'
                     'Correction in the third take.\r\n\r\n'
                     'This is test.\r\n\r\n')

        subscriber = self.app.data.find('subscribers', None, None)[0]
        seq, item = self._formatter.format(article, subscriber)[0]
        self.assertGreater(int(seq), 0)
        test_article = json.loads(item.get('data'))
        self.assertEqual(test_article['body_text'], body_text)

    def test_locator(self):
        article = {
            'source': 'AAP',
            'anpa_category': [{'qcode': 's'}],
            'headline': 'This is a test headline',
            'byline': 'joe',
            'slugline': 'slugline',
            'subject': [{'qcode': '15017000'}],
            'anpa_take_key': 'take_key',
            'unique_id': '1',
            'type': 'preformatted',
            'body_html': 'The story body',
            'word_count': '1',
            'priority': '1',
            'firstcreated': utcnow(),
            'versioncreated': utcnow(),
            'lock_user': ObjectId(),
            'place': [{'qcode': 'VIC', 'name': 'VIC'}]
        }

        subscriber = self.app.data.find('subscribers', None, None)[0]
        seq, item = self._formatter.format(article, subscriber)[0]
        self.assertGreater(int(seq), 0)
        test_article = json.loads(item.get('data'))
        self.assertEqual(test_article['headline'], 'This is a test headline')
        self.assertEqual(test_article['place'][0]['qcode'], 'CRIK')
        article['anpa_category'] = [{'qcode': 'a'}]
        article['place'] = [{'qcode': 'VIC', 'name': 'VIC'}]
        seq, item = self._formatter.format(article, subscriber)[0]
        self.assertGreater(int(seq), 0)
        test_article = json.loads(item.get('data'))
        self.assertEqual(test_article['headline'], 'This is a test headline')
        self.assertEqual(test_article['place'][0]['qcode'], 'VIC')

    def test_body_footer(self):
        article = {
            'source': 'AAP',
            'anpa_category': [{'qcode': 's'}],
            'headline': 'This is a test headline',
            'byline': 'joe',
            'slugline': 'slugline',
            'subject': [{'qcode': '15017000'}],
            'anpa_take_key': 'take_key',
            'unique_id': '1',
            'type': 'preformatted',
            'body_html': 'The story body',
            'word_count': '1',
            'priority': '1',
            'firstcreated': utcnow(),
            'versioncreated': utcnow(),
            'lock_user': ObjectId(),
            'body_footer': 'call helpline 999 if you are planning to quit smoking'
        }

        subscriber = self.app.data.find('subscribers', None, None)[0]
        seq, item = self._formatter.format(article, subscriber)[0]

        formatted_article = json.loads(item.get('data'))
        self.assertEqual(formatted_article['body_text'],
                         'The story body call helpline 999 if you are planning to quit smoking')
