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

from test_factory import SuperdeskTestCase
from apps.publish import init_app
from apps.publish.formatters.aap_ipnews_formatter import AAPIpNewsFormatter
from apps.publish.formatters.aap_formatter_common import set_subject


class AapIpNewsFormatterTest(SuperdeskTestCase):
    subscribers = [{"_id": "1", "name": "ipnews", "subscriber_type": SUBSCRIBER_TYPES.WIRE, "media_type": "media",
                    "is_active": True, "sequence_num_settings": {"max": 10, "min": 1},
                    "destinations": [{"name": "AAP IPNEWS", "delivery_type": "email", "format": "AAP IPNEWS",
                                      "config": {"recipients": "test@sourcefabric.org"}
                                      }]
                    }]

    desks = [{'_id': 1, 'name': 'National'},
             {'_id': 2, 'name': 'Sports'},
             {'_id': 3, 'name': 'Finance'}]

    article = {
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
        'priority': 1,
        'place': [{'qcode': 'VIC', 'name': 'VIC'}]
    }

    vocab = [{'_id': 'categories', 'items': [
        {'is_active': True, 'name': 'Overseas Sport', 'qcode': 'S', 'subject': '15000000'},
        {'is_active': True, 'name': 'Finance', 'qcode': 'F', 'subject': '04000000'}
    ]}, {'_id': 'geographical_restrictions', 'items': [{'name': 'New South Wales', 'value': 'NSW', 'is_active': True},
                                                       {'name': 'Victoria', 'value': 'VIC', 'is_active': True}]}]

    def setUp(self):
        super().setUp()
        self.app.data.insert('subscribers', self.subscribers)
        self.app.data.insert('vocabularies', self.vocab)
        self.app.data.insert('desks', self.desks)
        init_app(self.app)

    def testIPNewsFormatter(self):
        subscriber = self.app.data.find('subscribers', None, None)[0]

        f = AAPIpNewsFormatter()
        seq, item = f.format(self.article, subscriber)[0]

        self.assertGreater(int(seq), 0)
        self.assertEqual(seq, item['sequence'])
        item.pop('sequence')
        self.assertDictEqual(item,
                             {'category': 'a', 'texttab': 't', 'fullStory': 1, 'ident': '0',
                              'headline': 'VIC:This is a test headline', 'service_level': 'a', 'originator': 'AAP',
                              'take_key': 'take_key', 'article_text': 'The story body', 'priority': 'f', 'usn': '1',
                              'subject_matter': 'international law', 'news_item_type': 'News',
                              'subject_reference': '02011001', 'subject': 'crime, law and justice',
                              'wordcount': '1', 'subject_detail': 'international court or tribunal',
                              'genre': 'Current', 'keyword': 'slugline', 'author': 'joe'})

    def testIPNewsHtmlToText(self):
        article = {
            'source': 'AAP',
            'anpa_category': [{'qcode': 'a'}],
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
            'priority': 1
        }

        subscriber = self.app.data.find('subscribers', None, None)[0]

        f = AAPIpNewsFormatter()
        seq, item = f.format(article, subscriber)[0]

        expected = '\r\nThe story body line 1 \r\nLine 2 \r\n\r\nabcdefghi abcdefghi abcdefghi abcdefghi ' \
                   'abcdefghi abcdefghi abcdefghi abcdefghi \r\nmore'
        self.assertEqual(item['article_text'], expected)

    def testMultipleCategories(self):
        article = {
            'source': 'AAP',
            'anpa_category': [{'name': 'Finance', 'qcode': 'F'},
                              {'name': 'Overseas Sport', 'qcode': 'S'}],
            'headline': 'This is a test headline',
            'byline': 'joe',
            'slugline': 'slugline',
            'subject': [{'qcode': '04001005'}, {'qcode': '15011002'}],
            'anpa_take_key': 'take_key',
            'unique_id': '1',
            'type': 'text',
            'body_html': 'body',
            'word_count': '1',
            'priority': 1,
            'task': {'desk': 1},
            'place': [{'qcode': 'VIC', 'name': 'VIC'}]
        }

        subscriber = self.app.data.find('subscribers', None, None)[0]

        f = AAPIpNewsFormatter()
        docs = f.format(article, subscriber)
        self.assertEqual(len(docs), 2)
        for seq, doc in docs:
            if doc['category'] == 'S':
                self.assertEqual(doc['subject_reference'], '15011002')
                self.assertEqual(doc['subject_detail'], 'four-man sled')
                self.assertEqual(doc['headline'], 'VIC:This is a test headline')
            if doc['category'] == 'F':
                self.assertEqual(doc['subject_reference'], '04001005')
                self.assertEqual(doc['subject_detail'], 'viniculture')
                self.assertEqual(doc['headline'], 'VIC:This is a test headline')
                codes = set(doc['selector_codes'].split(' '))
                expected_codes = set('cxx 0fh axx az and pxx 0ah 0ir 0px 0hw pnd pxd cnd cxd 0nl axd'.split(' '))
                self.assertSetEqual(codes, expected_codes)

    def testGeoBlock(self):
        article = {
            'source': 'AAP',
            'anpa_category': [{'qcode': 'a'}],
            'headline': 'This is a test headline',
            'byline': 'joe',
            'slugline': 'slugline',
            'subject': [{'qcode': '04001005'}, {'qcode': '15011002'}],
            'anpa_take_key': 'take_key',
            'unique_id': '1',
            'type': 'text',
            'body_html': 'body',
            'word_count': '1',
            'priority': 1,
            'task': {'desk': 1},
            'urgency': 1,
            'place': [{'qcode': 'VIC', 'name': 'VIC'}],
            'targeted_for': [{'name': 'New South Wales', 'allow': False}, {'name': 'Victoria', 'allow': True}]
        }

        subscriber = self.app.data.find('subscribers', None, None)[0]

        f = AAPIpNewsFormatter()
        seq, doc = f.format(article, subscriber)[0]
        codes = set(doc['selector_codes'].split(' '))
        expected_codes_str = 'an5 an4 an7 an6 ax5 an3 ax6 ax7 0hw an8 0ir px6 ax4 ax3 ax8 px5 0ah 0px px3 az'
        expected_codes_str += ' px8 0fh px7 px4 pn3 pn4 pn5 pn6 pn7 px0'
        expected_codes = set(expected_codes_str.split(' '))
        self.assertSetEqual(codes, expected_codes)

    def testGeoBlockNotTwoStates(self):
        article = {
            'source': 'AAP',
            'anpa_category': [{'qcode': 'a'}],
            'headline': 'This is a test headline',
            'byline': 'joe',
            'slugline': 'slugline',
            'subject': [{'qcode': '04001005'}, {'qcode': '15011002'}],
            'anpa_take_key': 'take_key',
            'unique_id': '1',
            'type': 'text',
            'body_html': 'body',
            'word_count': '1',
            'priority': 1,
            'task': {'desk': 1},
            'urgency': 1,
            'place': [{'qcode': 'VIC', 'name': 'VIC'}],
            'targeted_for': [{'name': 'New South Wales', 'allow': False}, {'name': 'Victoria', 'allow': False}]
        }

        subscriber = self.app.data.find('subscribers', None, None)[0]

        f = AAPIpNewsFormatter()
        seq, doc = f.format(article, subscriber)[0]
        codes = set(doc['selector_codes'].split(' '))
        expected_codes_str = 'an5 an4 an7 an6 ax5 ax6 ax7 an8 px6 ax4 ax8 px5 0ah 0px'
        expected_codes_str += ' px8 0fh px7 px4 pn4 pn5 pn6 pn7 px0'
        expected_codes = set(expected_codes_str.split(' '))
        self.assertSetEqual(codes, expected_codes)

    def testIpNewsFormatterNoSubject(self):
        article = {
            'source': 'AAP',
            'anpa_category': [{'qcode': 'a'}],
            'headline': 'This is a test headline',
            'byline': 'joe',
            'slugline': 'slugline',
            'subject': [],
            'anpa_take_key': 'take_key',
            'unique_id': '1',
            'type': 'text',
            'body_html': 'body',
            'word_count': '1',
            'priority': 1,
            'task': {'desk': 1},
            'urgency': 1,
            'place': [{'qcode': 'VIC', 'name': 'VIC'}]
        }
        subscriber = self.app.data.find('subscribers', None, None)[0]

        f = AAPIpNewsFormatter()
        seq, doc = f.format(article, subscriber)[0]
        self.assertEqual(doc['subject_reference'], '00000000')
        self.assertEqual(doc['headline'], 'VIC:This is a test headline')

        article = {
            'source': 'AAP',
            'anpa_category': [{'qcode': 'a'}],
            'headline': 'This is a test headline',
            'byline': 'joe',
            'slugline': 'slugline',
            'subject': None,
            'anpa_take_key': 'take_key',
            'unique_id': '1',
            'type': 'text',
            'body_html': 'body',
            'word_count': '1',
            'priority': 1,
            'task': {'desk': 1},
            'urgency': 1,
            'place': None
        }

        seq, doc = f.format(article, subscriber)[0]
        self.assertEqual(doc['subject_reference'], '00000000')
        self.assertEqual(doc['headline'], 'This is a test headline')


class DefaultSubjectTest(SuperdeskTestCase):

    def setUp(self):
        super().setUp()
        vocabularies = [{
            '_id': 'categories',
            'display_name': 'Categories',
            'type': 'manageable',
            'items': [
                {'is_active': True, 'name': 'Australian General News', 'qcode': 'a'},
                {'is_active': True, 'name': 'Australian Weather', 'qcode': 'b', 'subject': '17000000'},
                {'is_active': True, 'name': 'General Features', 'qcode': 'c'},
                {'is_active': False, 'name': 'Reserved (obsolete/unused)', 'qcode': 'd'},
                {'is_active': True, 'name': 'Entertainment', 'qcode': 'e', 'subject': '01000000'},
                {'is_active': True, 'name': 'Finance', 'qcode': 'f', 'subject': '04000000'},
                {'is_active': False, 'name': 'SportSet', 'qcode': 'g'},
                {'is_active': True, 'name': 'FormGuide', 'qcode': 'h'},
                {'is_active': True, 'name': 'International News', 'qcode': 'i'},
                {'is_active': False, 'name': 'Reserved (obsolete/unused)', 'qcode': 'k'},
                {'is_active': True, 'name': 'Press Release Service', 'qcode': 'j'},
                {'is_active': True, 'name': 'Lotteries', 'qcode': 'l'},
                {'is_active': True, 'name': 'Line Check Messages', 'qcode': 'm'},
                {'is_active': False, 'name': 'Reserved', 'qcode': 'n'},
                {'is_active': True, 'name': 'State Parliaments', 'qcode': 'o', 'subject': '11000000'},
                {'is_active': True, 'name': 'Federal Parliament', 'qcode': 'p', 'subject': '11000000'},
                {'is_active': True, 'name': 'Stockset', 'qcode': 'q', 'subject': '04000000'},
                {'is_active': True, 'name': 'Racing (Turf)', 'qcode': 'r', 'subject': '15000000'},
                {'is_active': True, 'name': 'Overseas Sport', 'qcode': 's', 'subject': '15000000'},
                {'is_active': True, 'name': 'Domestic Sport', 'qcode': 't', 'subject': '15000000'},
                {'is_active': False, 'name': 'Reserved (Obsolete/unused)', 'qcode': 'u'},
                {'is_active': True, 'name': 'Advisories', 'qcode': 'v'},
                {'is_active': False, 'name': 'Reserved (Obsolete/unused)', 'qcode': 'w'},
                {'is_active': True, 'name': 'Special Events (olympics/ Aus elections)', 'qcode': 'x'},
                {'is_active': False, 'name': 'Special Events (obsolete/unused)', 'qcode': 'y'},
                {'is_active': False, 'name': 'Supplementary Traffic', 'qcode': 'z'}
            ]
        }]

        self.app.data.insert('vocabularies', vocabularies)
        init_app(self.app)

    def test_subject(self):
        article = {
            'anpa_category': [{'qcode': 'a'}, {'qcode': 's'}],
            'subject': [{'qcode': '04001005'}, {'qcode': '15011002'}]
        }

        self.assertEqual(set_subject({'qcode': 'a'}, article), '04001005')
        self.assertEqual(set_subject({'qcode': 's'}, article), '15011002')
        article = {
            'anpa_category': [{'qcode': 'a'}, {'qcode': 's'}],
            'subject': None
        }

        self.assertEqual(set_subject({'qcode': 'a'}, article), None)
        self.assertEqual(set_subject({'qcode': 's'}, article), None)

        article = {
            'anpa_category': None,
            'subject': [{'qcode': '04001005'}, {'qcode': '15011002'}]
        }

        self.assertEqual(set_subject(None, article), '04001005')
