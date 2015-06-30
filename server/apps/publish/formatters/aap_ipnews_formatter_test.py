# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.tests import TestCase
from apps.publish import init_app
from apps.publish.formatters.aap_ipnews_formatter import AAPIpNewsFormatter


class AapIpNewsFormatterTest(TestCase):
    subscribers = [{"_id": "1", "name": "Test", "can_send_takes_packages": False, "media_type": "media",
                    "is_active": True, "sequence_num_settings": {"max": 10, "min": 1},
                    "destinations": [{"name": "AAP IPNEWS", "delivery_type": "email", "format": "AAP IPNEWS",
                                      "config": {"recipients": "test@sourcefabric.org"}
                                      }]
                    }]

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
        'priority': '1'
    }

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.app.data.insert('subscribers', self.subscribers)
            init_app(self.app)

    def TestIPNewsFormatter(self):
        with self.app.app_context():
            subscriber = self.app.data.find('subscribers', None, None)[0]

            f = AAPIpNewsFormatter()
            seq, item = f.format(self.article, subscriber)

            self.assertGreater(int(seq), 0)
            self.assertEquals(seq, item['sequence'])
            item.pop('sequence')
            self.assertDictEqual(item,
                                 {'category': 'a', 'texttab': 't', 'fullStory': 1, 'ident': '0',
                                  'headline': 'This is a test headline', 'service_level': 'a', 'originator': 'AAP',
                                  'take_key': 'take_key', 'article_text': 'The story body', 'priority': '1', 'usn': '1',
                                  'subject_matter': 'international law', 'news_item_type': 'News',
                                  'subject_reference': '02011001', 'subject': 'crime, law and justice',
                                  'wordcount': '1', 'subject_detail': 'international court or tribunal',
                                  'genre': 'Current', 'keyword': 'slugline', 'author': 'joe',
                                  'selector_codes': '3**'})

    def TestIPNewsHtmlToText(self):
        article = {
            'source': 'AAP',
            'anpa-category': {'qcode': 'a'},
            'headline': 'This is a test headline',
            'byline': 'joe',
            'slugline': 'slugline',
            'subject': [{'qcode': '02011001'}],
            'anpa_take_key': 'take_key',
            'unique_id': '1',
            'type': 'text',
            'body_html': '<p>The story body line 1<br>Line 2</p>\
                         <p>abcdefghi abcdefghi abcdefghi abcdefghi abcdefghi abcdefghi abcdefghi abcdefghi more</p>',
            'word_count': '1',
            'priority': '1'
        }

        with self.app.app_context():
            subscriber = self.app.data.find('subscribers', None, None)[0]

            f = AAPIpNewsFormatter()
            seq, item = f.format(article, subscriber)

            expected = '\r\nThe story body line 1 \r\nLine 2 \r\n\r\nabcdefghi abcdefghi abcdefghi abcdefghi ' \
                       'abcdefghi abcdefghi abcdefghi abcdefghi \r\nmore'
            self.assertEquals(item['article_text'], expected)
