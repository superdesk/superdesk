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
import superdesk
from apps.publish import init_app
from superdesk.publish.odbc import ODBCPublishService


class ODBCTests(TestCase):
    queue_items = [{'_id': '1',
                    'output_channel_id': '1',
                    'destination': {
                        'delivery_type': 'ftp',
                        'config': {},
                        'name': 'destination1'
                    },
                    'formatted_item_id': '1',
                    'subscriber_id': '1',
                    'state': 'in-progress',
                    'item_id': 1
                    }]

    formatted_item = {
        '_id': '1',
        'item_id': 'tag:localhost:2015:8357d2dd-dcd0-49ac-91ba-2339cb568a46',
        'item_version': 0,
        'format': 'AAP IPNEWS',
        'formatted_item': {
            'ident': '0',
            'wordcount': 313,
            'texttab': 'x',
            'selector_codes': 'PXX',
            'originator': 'AAP',
            'service_level': 'a',
            'keyword': 'ROSS',
            'subject': 'crime, law and justice',
            'category': 'a',
            'take_key': None,
            'subject_detail': 'international court or tribunal',
            'subject_reference': '02011001',
            'article_text': 'THIS IS A TEST PLEASE IGNORE',
            'priority': None,
            'headline': 'TEST HEADLINE',
            'usn': 68147,
            'subject_matter': 'international law',
            'sequence': 117,
            'news_item_type': 'News',
            'author': '',
            'genre': 'Current',
            'fullStory': 1
        },
        "published_seq_num": 117,
    }

    output_channel = [{'_id': '1',
                       'name': 'OC1',
                       'description': 'Testing...',
                       'channel_type': 'metadata',
                       'is_active': True,
                       'format': 'AAP IPNEWS'
                       }]

    subscriber = [{'_id': '1',
                   'is_active': True,
                   'name': 'TestSub',
                   'subscriber_type': 'media',
                   'critical_errors': {'9004': True}}]

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.app.data.insert('output_channels', self.output_channel)
            self.app.data.insert('subscribers', self.subscriber)
            self.app.data.insert('publish_queue', self.queue_items)
            init_app(self.app)

    def test_transmit(self):
        if superdesk.app.config['ODBC_PUBLISH']:
            with self.app.app_context():
                subscriber = self.app.data.find('subscribers', None, None)[0]
                output_channel = self.app.data.find('output_channels', None, None)[0]
                output_channel['config'] = {
                    'connection_string': superdesk.app.config['ODBC_TEST_CONNECTION_STRING'],
                    'stored_procedure': 'InsertNews'}
                publish_service = ODBCPublishService()
                ret = publish_service._transmit(self.formatted_item, subscriber, output_channel)
                self.assertGreater(ret, 0)
