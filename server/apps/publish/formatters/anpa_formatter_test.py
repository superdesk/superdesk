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
from apps.publish.formatters.anpa_formatter import AAPAnpaFormatter
from datetime import datetime
import io


class ANPAFormatterTest(TestCase):
    output_channel = [{'_id': '1',
                       'name': 'OC1',
                       'description': 'Testing...',
                       'channel_type': 'metadata',
                       'is_active': True,
                       'format': 'ANPA'}]
    article = {
        'source': 'AAP',
        '_updated': datetime.strptime('2015-05-29 05:46', '%Y-%m-%d %H:%M'),
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

    def TestANPAFormatter(self):
        with self.app.app_context():
            output_channel = self.app.data.find('output_channels', None, None)[0]
            f = AAPAnpaFormatter()
            seq, item = f.format(self.article, output_channel, self.sel_codes)
            self.assertGreater(int(seq), 0)

            lines = io.StringIO(item.decode())
            line = lines.readline()
            self.assertEqual(line.strip(), 'aaa bbb')
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
