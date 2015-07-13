# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from apps.publish.subscribers import SUBSCRIBER_TYPES

from superdesk.tests import TestCase
from apps.publish import init_app
from apps.publish.formatters.aap_bulletinbuilder_formatter import AAPBulletinBuilderFormatter
from superdesk.utils import json_serialize_datetime_objectId
from superdesk import json
from superdesk.utc import utcnow
from bson import ObjectId


class AapBulletinBuilderFormatterTest(TestCase):
    subscribers = [{"_id": "1", "name": "Test", "subscriber_type": SUBSCRIBER_TYPES.WIRE, "media_type": "media",
                    "is_active": True, "sequence_num_settings": {"max": 10, "min": 1},
                    "destinations": [{"name": "AAP Bulletin Builder", "delivery_type": "pull",
                                      "format": "AAP BULLETIN BUILDER"
                                      }]
                    }]

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.app.data.insert('subscribers', self.subscribers)
            init_app(self.app)

    def TestBulletinBuilderFormatter(self):
        article = {
            'source': 'AAP',
            'anpa-category': {'qcode': 'a'},
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

        with self.app.app_context():
            subscriber = self.app.data.find('subscribers', None, None)[0]
            f = AAPBulletinBuilderFormatter()
            seq, item = f.format(article, subscriber)[0]
            self.assertGreater(int(seq), 0)
            self.assertEqual(json.dumps(article, default=json_serialize_datetime_objectId), item)

    def TestStripHtml(self):
        article = {
            'source': 'AAP',
            'headline': 'This is a test headline',
            'body_html': ('<p>The story body line 1<br>Line 2</p>'
                          '<p>abcdefghi abcdefghi abcdefghi abcdefghi abcdefghi'
                          '<span> abcdefghi</span> abcdefghi abcdefghi more</p>'
                          '<table><tr><td>test</td></tr></table>')
        }

        body_text = ('The story body line 1 Line 2\r\n\r\n'
                     'abcdefghi abcdefghi abcdefghi abcdefghi abcdefghi'
                     ' abcdefghi abcdefghi abcdefghi more\r\n\r\n'
                     'test')

        with self.app.app_context():
            subscriber = self.app.data.find('subscribers', None, None)[0]
            f = AAPBulletinBuilderFormatter()
            seq, item = f.format(article, subscriber)[0]
            self.assertGreater(int(seq), 0)
            test_article = json.loads(item)
            self.assertEqual(test_article['body_text'], body_text)
