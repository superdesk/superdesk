# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from test_factory import SuperdeskTestCase
from apps.publish import init_app
from apps.publish.formatters.aap_sms_formatter import AAPSMSFormatter


class AapSMSFormatterTest(SuperdeskTestCase):
    subscribers = [{"_id": "1", "name": "Test", "can_send_takes_packages": False, "media_type": "media",
                    "is_active": True, "sequence_num_settings": {"max": 10, "min": 1},
                    "destinations": [{"name": "AAP SMS", "delivery_type": "ODBC", "format": "AAP SMS",
                                      "config": {"connection_string": "DRIVER=BLAH", "stored_procedure": "Insert"}
                                      }]
                    }]

    article = {
        'priority': 1,
        'anpa_category': [{'qcode': 'a'}],
        'headline': 'This is a test headline',
        'type': 'text',
        'body_html': 'The story body',
        'body_footer': 'call helpline 999 if you are planning to quit smoking'
    }

    def setUp(self):
        super().setUp()
        self.app.data.insert('subscribers', self.subscribers)
        init_app(self.app)

    def TestSMSFormatter(self):
        subscriber = self.app.data.find('subscribers', None, None)[0]

        f = AAPSMSFormatter()
        seq, item = f.format(self.article, subscriber)[0]

        self.assertGreater(int(seq), 0)
        self.assertDictEqual(item, {'Category': 'a', 'Priority': 'f', 'Sequence': item['Sequence'], 'ident': '0',
                                    'Headline': 'This is a test headline',
                                    'StoryText':
                                        'The story bodycall helpline 999 if you are planning to quit smoking'})
