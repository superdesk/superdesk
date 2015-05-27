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
    output_channel = [{'_id': '1',
                       'name': 'OC1',
                       'description': 'Testing...',
                       'channel_type': 'metadata',
                       'is_active': True,
                       'format': 'nitf'}]
    article = {
        'originator': 'AAP',
        'anpa-category': {'qcode': 'a'},
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
    sel_codes = {'1': ['aaa', 'bbb']}

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.app.data.insert('output_channels', self.output_channel)
            init_app(self.app)

    def TestIPNewsFormatter(self):
        with self.app.app_context():
            output_channel = self.app.data.find('output_channels', None, None)[0]
            f = AAPIpNewsFormatter()
            seq, item = f.format(self.article, output_channel, self.sel_codes)
            self.assertGreater(int(seq), 0)
            self.assertEquals(seq, item['sequence'])
            item.pop('sequence')
            self.assertDictEqual(item,
                                 {'category': 'a', 'texttab': 'x', 'fullStory': 1, 'ident': '0',
                                  'headline': 'This is a test headline', 'selector_codes': 'aaa bbb',
                                  'service_level': 'a', 'originator': 'AAP', 'take_key': 'take_key',
                                  'article_text': 'The story body', 'priority': '1', 'usn': '1',
                                  'subject_matter': 'international law', 'news_item_type': 'News',
                                  'subject_reference': '02011001', 'subject': 'crime, law and justice',
                                  'wordcount': '1', 'subject_detail': 'international court or tribunal',
                                  'genre': 'Current', 'keyword': 'slugline', 'author': 'joe'})
