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
from apps.publish.formatters.anpa_formatter import AAPAnpaFormatter
from datetime import datetime
import io


class ANPAFormatterTest(TestCase):
    subscribers = [{"_id": "1", "name": "Test", "subscriber_type": SUBSCRIBER_TYPES.WIRE, "media_type": "media",
                    "is_active": True, "sequence_num_settings": {"max": 10, "min": 1},
                    "destinations": [{"name": "ANPA", "delivery_type": "email", "format": "ANPA",
                                      "config": {"recipients": "test@sourcefabric.org"}
                                      }]
                    }]

    article = {
        'source': 'AAP',
        '_updated': datetime.strptime('2015-05-29 05:46', '%Y-%m-%d %H:%M'),
        'anpa_category': [{'qcode': 'a'}],
        'headline': 'This is a test headline',
        'byline': 'joe',
        'slugline': 'slugline',
        'subject': [{'qcode': '02011001'}],
        'anpa_take_key': 'take_key',
        'unique_id': '1',
        'type': 'preformatted',
        'body_html': 'The story body',
        'type': 'text',
        'word_count': '1',
        'priority': '1'
    }

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.app.data.insert('subscribers', self.subscribers)
            init_app(self.app)

    def TestANPAFormatter(self):
        with self.app.app_context():
            subscriber = self.app.data.find('subscribers', None, None)[0]

            f = AAPAnpaFormatter()
            seq, item = f.format(self.article, subscriber)[0]

            self.assertGreater(int(seq), 0)

            lines = io.StringIO(item.decode())

            line = lines.readline()
            self.assertEqual(line[:3], '')  # Skip the sequence

            line = lines.readline()
            self.assertEqual(line[0:20], '1 a bc-slugline   ')  # skip the date

            line = lines.readline()
            self.assertEqual(line.strip(), 'This is a test headline')

            line = lines.readline()
            self.assertEqual(line.strip(), 'slugline take_key')

            line = lines.readline()
            self.assertEqual(line.strip(), 'The story body')

            line = lines.readline()
            self.assertEqual(line.strip(), 'AAP')

    def TestMultipleCategoryFormatter(self):
        with self.app.app_context():
            subscriber = self.app.data.find('subscribers', None, None)[0]
            multi_article = dict(self.article)
            multi_article.pop('anpa_category')
            multi_article['anpa_category'] = [{'qcode': 'a'}, {'qcode': 'b'}]
            f = AAPAnpaFormatter()
            docs = f.format(multi_article, subscriber)
            self.assertEqual(len(docs), 2)
            cat = 'a'
            for seq, doc in docs:
                lines = io.StringIO(doc.decode())
                line = lines.readline()
                line = lines.readline()
                self.assertEqual(line[2:3], cat)  # skip the date
                cat = 'b'

    def test_process_headline_empty_sequence_short_headline(self):
        f = AAPAnpaFormatter()
        article = {'headline': '1234567890' * 5}
        anpa = []
        f._process_headline(anpa, article)
        self.assertEqual(anpa[0], b'12345678901234567890123456789012345678901234567890')

    def test_process_headline_empty_sequence_long_headline(self):
        f = AAPAnpaFormatter()
        article = {'headline': '1234567890' * 7}
        anpa = []
        f._process_headline(anpa, article)
        self.assertEqual(anpa[0], b'1234567890123456789012345678901234567890123456789012345678901234')

    def test_process_headline_with_sequence_short_headline(self):
        f = AAPAnpaFormatter()
        article = {'headline': '1234567890=7', 'sequence': 7}
        anpa = []
        f._process_headline(anpa, article)
        self.assertEqual(anpa[0], b'1234567890=7')

    def test_process_headline_with_sequence_long_headline(self):
        f = AAPAnpaFormatter()
        article1 = {'headline': '1234567890' * 7 + '=7', 'sequence': 7}
        anpa = []
        f._process_headline(anpa, article1)
        self.assertEqual(anpa[0], b'12345678901234567890123456789012345678901234567890123456789012=7')
        article2 = {'headline': '1234567890' * 7 + '=7', 'sequence': 17}
        anpa = []
        f._process_headline(anpa, article2)
        self.assertEqual(anpa[0], b'1234567890123456789012345678901234567890123456789012345678901=17')
