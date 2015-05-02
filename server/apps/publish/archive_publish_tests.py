# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.tests import TestCase
from apps.publish import init_app, archive_publish, publish_queue
from superdesk.utc import utcnow
from datetime import timedelta
import superdesk


class ArchivePublishTestCase(TestCase):
    subscribers = [{'_id': 1, 'name': 'sub1', 'is_active': True, 'destinations': [{
                    'name': 'dest1',
                    'delivery_type': 'ftp',
                    'config': {'address': '127.0.0.1', 'username': 'test'}}]},
                   {'_id': 2, 'name': 'sub1', 'is_active': True, 'destinations': [{
                    'name': 'dest2',
                    'delivery_type': 'file copy',
                    'config': {'address': '/share/copy'}}, {
                       'name': 'dest3',
                       'delivery_type': 'Email',
                       'config': {'address': 'send@gmail.com'}}]}]

    output_channels = [{'_id': 1, 'name': 'oc1', 'is_active': True, 'format': 'nitf', 'destinations': [1]},
                       {'_id': 2, 'name': 'oc2', 'is_active': False, 'format': 'nitf', 'destinations': [1, 2]},
                       {'_id': 3, 'name': 'oc3', 'is_active': True, 'format': 'anpa', 'destinations': [2]},
                       {'_id': 4, 'name': 'oc4', 'is_active': True, 'format': 'nitf', 'destinations': [2]}]

    destination_groups = [{'_id': 1, 'name': 'dg1'},
                          {'_id': 2, 'name': 'dg2', 'destination_groups': [1]},
                          {'_id': 3, 'name': 'dg3',
                           'output_channels': [{'channel': 1, 'selector_codes': ['A', 'B']}]},
                          {'_id': 4, 'name': 'dg4',
                           'output_channels': [{'channel': 1, 'selector_codes': ['Y']},
                                               {'channel': 2, 'selector_codes': ['X', 'B']},
                                               {'channel': 4}]},
                          {'_id': 5, 'name': 'dg5',
                           'output_channels': [{'channel': 2, 'selector_codes': ['A']},
                                               {'channel': 3, 'selector_codes': ['X', 'y']}]}]

    articles = [{'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4f9',
                 '_id': 1,
                 'last_version': 3,
                 'body_html': 'Test body',
                 'destination_groups': [4],
                 'urgency': 4,
                 'headline': 'Two students missing',
                 'pubstatus': 'done',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'ednote': 'Andrew Marwood contributed to this article',
                 'dateline': 'Sydney',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject':[{'qcode': '17004000', 'name': 'Statistics'},
                            {'qcode': '04001002', 'name': 'Weather'}],
                 'expiry': utcnow() + timedelta(minutes=20)},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a974-xy4532fe33f9',
                 '_id': 2,
                 'last_version': 3,
                 'body_html': 'Test body of the second article',
                 'destination_groups': [4],
                 'urgency': 4,
                 'headline': 'Another two students missing',
                 'pubstatus': 'done',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'ednote': 'Andrew Marwood contributed to this article',
                 'dateline': 'Sydney',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject':[{'qcode': '17004000', 'name': 'Statistics'},
                            {'qcode': '04001002', 'name': 'Weather'}],
                 'expiry': utcnow() + timedelta(minutes=20),
                 'publish_schedule': "2015-05-30T10:00:00+0000"}]

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.app.data.insert('output_channels', self.output_channels)
            self.app.data.insert('subscribers', self.subscribers)
            self.app.data.insert('destination_groups', self.destination_groups)
            self.app.data.insert('archive', self.articles)
            init_app(self.app)

    def test_resolve_destination_groups(self):
        with self.app.app_context():
            resolved_destination_groups = archive_publish.ArchivePublishService().resolve_destination_groups([2])
            self.assertEquals(2, len(resolved_destination_groups))

    def test_resolve_output_channels(self):
        with self.app.app_context():
            resolved_destination_groups = archive_publish.ArchivePublishService().resolve_destination_groups([4])
            dgs = list(resolved_destination_groups.values())
            resolved_output_channels, selector_codes, formatters = \
                archive_publish.ArchivePublishService().resolve_output_channels(dgs)
            self.assertEquals(3, len(resolved_output_channels))
            self.assertTrue(2 in resolved_output_channels)

            self.assertTrue(1 in selector_codes)
            self.assertTrue(2 in selector_codes)
            self.assertTrue('Y' in selector_codes[1])
            self.assertTrue('X' in selector_codes[2])
            self.assertTrue('B' in selector_codes[2])

            self.assertEquals(1, len(formatters))
            self.assertTrue('nitf' in formatters)

    def test_resolve_output_channels_flattened(self):
        with self.app.app_context():
            resolved_destination_groups2 = archive_publish.ArchivePublishService().resolve_destination_groups([3])
            dgs = list(resolved_destination_groups2.values())
            resolved_output_channels, selector_codes, formatters = \
                archive_publish.ArchivePublishService().resolve_output_channels(dgs)
            self.assertEquals(1, len(resolved_output_channels))
            self.assertTrue(1 in resolved_output_channels)

            self.assertTrue(1 in selector_codes)
            self.assertTrue('A' in selector_codes[1])
            self.assertTrue('B' in selector_codes[1])

            self.assertEquals(1, len(formatters))
            self.assertTrue('nitf' in formatters)

    def test_get_subscribers(self):
        with self.app.app_context():
            resolved_destination_groups = archive_publish.ArchivePublishService().resolve_destination_groups([4])
            dgs = list(resolved_destination_groups.values())
            resolved_output_channels, selector_codes, formatters = \
                archive_publish.ArchivePublishService().resolve_output_channels(dgs)
            subscribers = archive_publish.ArchivePublishService().get_subscribers(resolved_output_channels[1])
            self.assertEquals(1, subscribers.count())

            subscribers = archive_publish.ArchivePublishService().get_subscribers(resolved_output_channels[2])
            self.assertEquals(2, subscribers.count())

    def test_queue_transmission(self):
        with self.app.app_context():
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(0, queue_items.count())
            archive_publish.ArchivePublishService().queue_transmission(self.articles[0])
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(6, queue_items.count())

    def test_queue_transmission_for_scheduled_publish(self):
        with self.app.app_context():
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(0, queue_items.count())
            archive_publish.ArchivePublishService().queue_transmission(self.articles[1])
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(6, queue_items.count())
            self.assertEquals("2015-05-30T10:00:00+0000", queue_items[0]["publish_schedule"])
            self.assertEquals("2015-05-30T10:00:00+0000", queue_items[1]["publish_schedule"])
            self.assertEquals("2015-05-30T10:00:00+0000", queue_items[2]["publish_schedule"])
            self.assertEquals("2015-05-30T10:00:00+0000", queue_items[3]["publish_schedule"])
            self.assertEquals("2015-05-30T10:00:00+0000", queue_items[4]["publish_schedule"])
            self.assertEquals("2015-05-30T10:00:00+0000", queue_items[5]["publish_schedule"])

    def test_delete_from_queue_by_article_id(self):
        with self.app.app_context():
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(0, queue_items.count())
            archive_publish.ArchivePublishService().queue_transmission(self.articles[1])
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(6, queue_items.count())
            publish_queue.PublishQueueService('publish_queue', superdesk.get_backend())\
                .delete_by_article_id(self.articles[1]['_id'])
            self.assertEquals(0, queue_items.count())
