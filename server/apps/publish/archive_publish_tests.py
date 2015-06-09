# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from datetime import timedelta

from eve.utils import config

from superdesk.tests import TestCase
from apps.publish import init_app, publish_queue, RemoveExpiredPublishContent
from apps.legal_archive import LEGAL_ARCHIVE_NAME, LEGAL_PUBLISH_QUEUE_NAME, LEGAL_FORMATTED_ITEM_NAME
from superdesk.utc import utcnow
from superdesk import get_resource_service
import superdesk


class ArchivePublishTestCase(TestCase):
    subscribers = [{'_id': '1', 'name': 'sub1', 'is_active': True, 'destinations': [{
                    'name': 'dest1',
                    'delivery_type': 'ftp',
                    'config': {'address': '127.0.0.1', 'username': 'test'}}]},
                   {'_id': '2', 'name': 'sub1', 'is_active': True, 'destinations': [{
                    'name': 'dest2',
                    'delivery_type': 'file copy',
                    'config': {'address': '/share/copy'}}, {
                       'name': 'dest3',
                       'delivery_type': 'Email',
                       'config': {'address': 'send@gmail.com'}}]}]

    output_channels = [{'_id': '1', 'name': 'oc1', 'is_active': True, 'format': 'nitf', 'destinations': ['1']},
                       {'_id': '2', 'name': 'oc2', 'is_active': False, 'format': 'nitf', 'destinations': ['1', '2']},
                       {'_id': '3', 'name': 'oc3', 'is_active': True, 'format': 'anpa', 'destinations': ['2']},
                       {'_id': '4', 'name': 'oc4', 'is_active': True,
                        'is_digital': True, 'format': 'nitf', 'destinations': ['2']}]

    destination_groups = [{'_id': '1', 'name': 'dg1'},
                          {'_id': '2', 'name': 'dg2', 'destination_groups': ['1']},
                          {'_id': '3', 'name': 'dg3',
                           'output_channels': [{'channel': '1', 'selector_codes': ['A', 'B']}]},
                          {'_id': '4', 'name': 'dg4',
                           'output_channels': [{'channel': '1', 'selector_codes': ['Y']},
                                               {'channel': '2', 'selector_codes': ['X', 'B']},
                                               {'channel': '4'}]},
                          {'_id': '5', 'name': 'dg5',
                           'output_channels': [{'channel': '2', 'selector_codes': ['A']},
                                               {'channel': '3', 'selector_codes': ['X', 'y']}]}]

    articles = [{'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4f9',
                 '_id': '1',
                 'type': 'text',
                 'last_version': 3,
                 '_version': 4,
                 'body_html': 'Test body',
                 'destination_groups': ['4'],
                 'urgency': 4,
                 'headline': 'Two students missing',
                 'pubstatus': 'usable',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'ednote': 'Andrew Marwood contributed to this article',
                 'dateline': 'Sydney',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject':[{'qcode': '17004000', 'name': 'Statistics'},
                            {'qcode': '04001002', 'name': 'Weather'}],
                 'state': 'published',
                 'expiry': utcnow() + timedelta(minutes=20)},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a974-xy4532fe33f9',
                 '_id': '2',
                 'last_version': 3,
                 '_version': 4,
                 'body_html': 'Test body of the second article',
                 'destination_groups': ['4'],
                 'urgency': 4,
                 'headline': 'Another two students missing',
                 'pubstatus': 'usable',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'ednote': 'Andrew Marwood contributed to this article',
                 'dateline': 'Sydney',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject':[{'qcode': '17004000', 'name': 'Statistics'},
                            {'qcode': '04001002', 'name': 'Weather'}],
                 'expiry': utcnow() + timedelta(minutes=20),
                 'state': 'scheduled',
                 'publish_schedule': "2016-05-30T10:00:00+0000",
                 'type': 'text'},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4fa',
                 '_id': '3',
                 'last_version': 3,
                 '_version': 4,
                 'body_html': 'Test body',
                 'destination_groups': ['4'],
                 'urgency': 4,
                 'headline': 'Two students missing killed',
                 'pubstatus': 'usable',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'ednote': 'Andrew Marwood contributed to this article killed',
                 'dateline': 'Sydney',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject':[{'qcode': '17004000', 'name': 'Statistics'},
                            {'qcode': '04001002', 'name': 'Weather'}],
                 'state': 'killed',
                 'expiry': utcnow() + timedelta(minutes=20),
                 'type': 'text'},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4fb',
                 '_id': '4',
                 'last_version': 3,
                 '_version': 4,
                 'body_html': 'Take-1 body',
                 'destination_groups': ['4'],
                 'urgency': 4,
                 'headline': 'Take-1 headline',
                 'abstract': 'Abstract for take-1',
                 'anpa-category': {'qcode': 'A', 'name': 'Sport'},
                 'pubstatus': 'done',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'dateline': 'Sydney',
                 'slugline': 'taking takes',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject':[{'qcode': '17004000', 'name': 'Statistics'},
                            {'qcode': '04001002', 'name': 'Weather'}],
                 'state': 'in-progress',
                 'expiry': utcnow() + timedelta(minutes=20),
                 'type': 'text'},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4fg',
                 '_id': '5',
                 'last_version': 3,
                 '_version': 4,
                 'body_html': 'Take-2 body',
                 'destination_groups': ['4'],
                 'urgency': 4,
                 'headline': 'Take-2 headline',
                 'abstract': 'Abstract for take-1',
                 'anpa-category': {'qcode': 'A', 'name': 'Sport'},
                 'pubstatus': 'done',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'dateline': 'Sydney',
                 'slugline': 'taking takes',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject':[{'qcode': '17004000', 'name': 'Statistics'},
                            {'qcode': '04001002', 'name': 'Weather'}],
                 'state': 'published',
                 'expiry': utcnow() + timedelta(minutes=20),
                 'type': 'text'},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4fc',
                 '_id': '6',
                 'last_version': 2,
                 '_version': 3,
                 'type': 'composite',
                 'groups': [{'id': 'root', 'refs': [{'idRef': 'main'}], 'role': 'grpRole:NEP'},
                            {
                                'id': 'main',
                                'refs': [
                                    {
                                        'location': 'archive',
                                        'guid': '5',
                                        'type': 'text'
                                    },
                                    {
                                        'location': 'archive',
                                        'guid': '4',
                                        'type': 'text'
                                    }
                                ],
                                'role': 'grpRole:main'}],
                 'firstcreated': utcnow(),
                 'expiry': utcnow() + timedelta(minutes=20)}]

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
            resolved_destination_groups = get_resource_service('archive_publish').resolve_destination_groups(['2'])
            self.assertEquals(2, len(resolved_destination_groups))

    def test_resolve_output_channels(self):
        with self.app.app_context():
            resolved_destination_groups = get_resource_service('archive_publish').resolve_destination_groups(['4'])
            dgs = list(resolved_destination_groups.values())
            resolved_output_channels, selector_codes, formatters = \
                get_resource_service('archive_publish').resolve_output_channels(dgs)
            self.assertEquals(3, len(resolved_output_channels))
            self.assertTrue('2' in resolved_output_channels)

            self.assertTrue('1' in selector_codes)
            self.assertTrue('2' in selector_codes)
            self.assertTrue('Y' in selector_codes['1'])
            self.assertTrue('X' in selector_codes['2'])
            self.assertTrue('B' in selector_codes['2'])

            self.assertEquals(1, len(formatters))
            self.assertTrue('nitf' in formatters)

    def test_resolve_output_channels_flattened(self):
        with self.app.app_context():
            resolved_destination_groups2 = get_resource_service('archive_publish').resolve_destination_groups(['3'])
            dgs = list(resolved_destination_groups2.values())
            resolved_output_channels, selector_codes, formatters = \
                get_resource_service('archive_publish').resolve_output_channels(dgs)
            self.assertEquals(1, len(resolved_output_channels))
            self.assertTrue('1' in resolved_output_channels)

            self.assertTrue('1' in selector_codes)
            self.assertTrue('A' in selector_codes['1'])
            self.assertTrue('B' in selector_codes['1'])

            self.assertEquals(1, len(formatters))
            self.assertTrue('nitf' in formatters)

    def test_get_subscribers(self):
        with self.app.app_context():
            resolved_destination_groups = get_resource_service('archive_publish').resolve_destination_groups(['4'])
            dgs = list(resolved_destination_groups.values())
            resolved_output_channels, selector_codes, formatters = \
                get_resource_service('archive_publish').resolve_output_channels(dgs)
            subscribers = get_resource_service('archive_publish').get_subscribers(resolved_output_channels['1'])
            self.assertEquals(1, subscribers.count())

            subscribers = get_resource_service('archive_publish').get_subscribers(resolved_output_channels['2'])
            self.assertEquals(2, subscribers.count())

    def test_queue_transmission(self):
        with self.app.app_context():
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(0, queue_items.count())
            get_resource_service('archive_publish').queue_transmission(self.articles[0])
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(6, queue_items.count())

    def test_queue_transmission_wrong_article_type_fails(self):
        with self.app.app_context():
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(0, queue_items.count())
            self.articles[0]['type'] = 'image'
            any_channel_closed, wrong_formatted_channels, queued = \
                get_resource_service('archive_publish').queue_transmission(self.articles[0])
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(0, queue_items.count())
            self.assertEquals(3, len(wrong_formatted_channels))
            self.assertFalse(queued)

            self.articles[0]['type'] = 'text'

    def test_queue_transmission_for_scheduled_publish(self):
        with self.app.app_context():
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(0, queue_items.count())
            get_resource_service('archive_publish').queue_transmission(self.articles[1])
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(6, queue_items.count())
            self.assertEquals("2016-05-30T10:00:00+0000", queue_items[0]["publish_schedule"])
            self.assertEquals("2016-05-30T10:00:00+0000", queue_items[1]["publish_schedule"])
            self.assertEquals("2016-05-30T10:00:00+0000", queue_items[2]["publish_schedule"])
            self.assertEquals("2016-05-30T10:00:00+0000", queue_items[3]["publish_schedule"])
            self.assertEquals("2016-05-30T10:00:00+0000", queue_items[4]["publish_schedule"])
            self.assertEquals("2016-05-30T10:00:00+0000", queue_items[5]["publish_schedule"])

    def test_queue_transmission_for_digital_channels(self):
        with self.app.app_context():
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(0, queue_items.count())
            get_resource_service('archive_publish').queue_transmission(self.articles[1], 'digital')
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(2, queue_items.count())
            self.assertEquals('4', queue_items[0]["output_channel_id"])
            self.assertEquals('4', queue_items[1]["output_channel_id"])

    def test_queue_transmission_for_wire_channels(self):
        with self.app.app_context():
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(0, queue_items.count())
            get_resource_service('archive_publish').queue_transmission(self.articles[1], 'wire')
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(4, queue_items.count())
            expected_output_channels = ['1', '2']
            self.assertIn(queue_items[0]["output_channel_id"], expected_output_channels)
            self.assertIn(queue_items[1]["output_channel_id"], expected_output_channels)
            self.assertIn(queue_items[2]["output_channel_id"], expected_output_channels)
            self.assertIn(queue_items[3]["output_channel_id"], expected_output_channels)

    def test_delete_from_queue_by_article_id(self):
        with self.app.app_context():
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(0, queue_items.count())

            get_resource_service('archive_publish').queue_transmission(self.articles[1])
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(6, queue_items.count())

            publish_queue.PublishQueueService('publish_queue', superdesk.get_backend())\
                .delete_by_article_id(self.articles[1]['_id'])
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(0, queue_items.count())

    def test_remove_published_expired_content(self):
        with self.app.app_context():
            published_service = get_resource_service('published')
            text_archive = get_resource_service('text_archive')
            legal_archive_service = get_resource_service(LEGAL_ARCHIVE_NAME)
            legal_publish_queue_service = get_resource_service(LEGAL_PUBLISH_QUEUE_NAME)
            legal_formatted_items_service = get_resource_service(LEGAL_FORMATTED_ITEM_NAME)

            original = self.articles[0].copy()
            get_resource_service('archive_publish').queue_transmission(original)
            published_service.post([original])

            published_items = published_service.get_other_published_items(original['item_id'])
            self.assertEquals(1, published_items.count())

            published_service.update_published_items(original['item_id'], 'expiry', utcnow() + timedelta(minutes=-60))
            RemoveExpiredPublishContent().run()
            published_items = published_service.get_other_published_items(str(original['item_id']))
            self.assertEquals(0, published_items.count())

            item = text_archive.find_one(req=None, _id=str(original['_id']))
            self.assertEquals(item['item_id'], self.articles[0]['_id'])

            legal_archive_doc = legal_archive_service.find_one(_id=self.articles[0]['_id'], req=None)
            self.assertIsNotNone(legal_archive_doc, 'Article cannot be none in Legal Archive')

            formatted_items = legal_formatted_items_service.get(None, {'item_id': self.articles[0]['_id']})
            self.assertGreaterEqual(formatted_items.count(), 1, 'Formatted Items must be greate than or equal to 1')
            for formatted_item in formatted_items:
                self.assertEquals(formatted_item['item_id'], self.articles[0]['_id'])
                self.assertEquals(formatted_item['item_version'], self.articles[0]['_version'])

            queue_items = legal_publish_queue_service.get(None, {'item_id': self.articles[0]['_id']})
            self.assertGreaterEqual(queue_items.count(), 1, 'Publish Queue Items must be greate than or equal to 1')

    def test_cannot_remove_scheduled_content(self):
        with self.app.app_context():
            published_service = get_resource_service('published')
            original = self.articles[1]

            published_service.post([original])
            published_items = published_service.get_other_published_items(original['item_id'])
            self.assertEquals(1, published_items.count())

            RemoveExpiredPublishContent().run()
            published_items = published_service.get_other_published_items(original['item_id'])
            self.assertEquals(1, published_items.count())

    def test_remove_killed_expired_content(self):
        with self.app.app_context():
            published_service = get_resource_service('published')
            text_archive = get_resource_service('text_archive')

            original = self.articles[2].copy()

            get_resource_service('archive_publish').queue_transmission(original)
            published_service.post([original])

            published_items = published_service.get_other_published_items(original['item_id'])
            self.assertEquals(1, published_items.count())

            published_service.update_published_items(original['item_id'], 'expiry', utcnow() + timedelta(minutes=-60))

            RemoveExpiredPublishContent().run()
            published_items = published_service.get_other_published_items(str(original['item_id']))
            self.assertEquals(0, published_items.count())

            item = text_archive.find_one(req=None, _id=str(original['_id']))
            self.assertIsNone(item)

    def test_remove_published_and_killed_expired_content(self):
        with self.app.app_context():
            published_service = get_resource_service('published')
            text_archive = get_resource_service('text_archive')

            published = self.articles[2].copy()
            published[config.CONTENT_STATE] = 'published'

            get_resource_service('archive_publish').queue_transmission(published)
            published_service.post([published])

            published_items = published_service.get_other_published_items(published['item_id'])
            self.assertEquals(1, published_items.count())

            killed = self.articles[2].copy()
            killed['_version'] += 1
            get_resource_service('archive_publish').queue_transmission(killed)
            published_service.post([killed])

            published_items = published_service.get_other_published_items(published['item_id'])
            self.assertEquals(2, published_items.count())

            published_service.update_published_items(killed['item_id'], 'expiry', utcnow() + timedelta(minutes=-60))
            RemoveExpiredPublishContent().run()

            published_items = published_service.get_other_published_items(killed['item_id'])
            self.assertEquals(0, published_items.count())

            item = text_archive.find_one(req=None, _id=str(published['_id']))
            self.assertIsNone(item)

            item = text_archive.find_one(req=None, _id=str(killed['_id']))
            self.assertIsNone(item)

    def test_processing_very_first_take(self):
        with self.app.app_context():

            original_package, updated_package = get_resource_service('archive_publish').process_takes(
                self.articles[4], self.articles[5]['_id'])

            self.assertIsNotNone(original_package)
            self.assertIsNotNone(updated_package)
            self.assertEqual(updated_package['body_html'], 'Take-2 body<br>')
            self.assertEqual(updated_package['headline'], 'Take-2 headline')

    def test_processing_second_take_where_first_take_published(self):
        with self.app.app_context():

            original_package, updated_package = get_resource_service('archive_publish').process_takes(
                self.articles[3], self.articles[5]['_id'])

            self.assertIsNotNone(original_package)
            self.assertIsNotNone(updated_package)
            self.assertEqual(updated_package['body_html'], 'Take-2 body<br>Take-1 body<br>')
            self.assertEqual(updated_package['headline'], 'Take-1 headline')
