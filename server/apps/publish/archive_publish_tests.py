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
import os
import json

from eve.utils import config
from eve.versioning import versioned_id_field
from apps.archive.archive import SOURCE as ARCHIVE
from apps.validators import ValidatorsPopulateCommand

from superdesk.tests import TestCase
from apps.publish import init_app, publish_queue, RemoveExpiredPublishContent
from apps.legal_archive import LEGAL_ARCHIVE_NAME, LEGAL_ARCHIVE_VERSIONS_NAME, LEGAL_PUBLISH_QUEUE_NAME, \
    LEGAL_FORMATTED_ITEM_NAME
from superdesk.utc import utcnow
from superdesk import get_resource_service
import superdesk


class ArchivePublishTestCase(TestCase):
    def init_data(self):
        self.subscribers = [{'_id': '1', 'name': 'sub1', 'is_active': True, 'destinations': [{
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

        self.output_channels = [{'_id': '1', 'name': 'oc1', 'is_active': True, 'format': 'nitf', 'destinations': ['1']},
                                {'_id': '2', 'name': 'oc2', 'is_active': False, 'format': 'nitf',
                                 'destinations': ['1', '2']},
                                {'_id': '3', 'name': 'oc3', 'is_active': True, 'format': 'anpa', 'destinations': ['2']},
                                {'_id': '4', 'name': 'oc4', 'is_active': True,
                                 'is_digital': True, 'format': 'nitf', 'destinations': ['2']}]

        self.destination_groups = [{'_id': '1', 'name': 'dg1'},
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

        self.articles = [{'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4f9',
                          '_id': '1',
                          'type': 'text',
                          'last_version': 3,
                          config.VERSION: 4,
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
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          'state': 'published',
                          'expiry': utcnow() + timedelta(minutes=20),
                          'unique_name': '#1'},
                         {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a974-xy4532fe33f9',
                          '_id': '2',
                          'last_version': 3,
                          config.VERSION: 4,
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
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          'expiry': utcnow() + timedelta(minutes=20),
                          'state': 'scheduled',
                          'publish_schedule': "2016-05-30T10:00:00+0000",
                          'type': 'text',
                          'unique_name': '#2'},
                         {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4fa',
                          '_id': '3',
                          'last_version': 3,
                          config.VERSION: 4,
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
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          'state': 'killed',
                          'expiry': utcnow() + timedelta(minutes=20),
                          'type': 'text',
                          'unique_name': '#3'},
                         {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4fb',
                          '_id': '4',
                          'last_version': 3,
                          config.VERSION: 4,
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
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          'state': 'in-progress',
                          'expiry': utcnow() + timedelta(minutes=20),
                          'type': 'text',
                          'unique_name': '#4'},
                         {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4fg',
                          '_id': '5',
                          'last_version': 3,
                          config.VERSION: 4,
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
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          'state': 'published',
                          'expiry': utcnow() + timedelta(minutes=20),
                          'type': 'text',
                          'unique_name': '#5'},
                         {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4fc',
                          '_id': '6',
                          'last_version': 2,
                          config.VERSION: 3,
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
                          'expiry': utcnow() + timedelta(minutes=20),
                          'unique_name': '#6'}]

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.init_data()
            self.app.data.insert('output_channels', self.output_channels)
            self.app.data.insert('subscribers', self.subscribers)
            self.app.data.insert('destination_groups', self.destination_groups)
            self.app.data.insert('archive', self.articles)
            self.filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), "validators.json")
            self.json_data = [{"_id": "kill", "schema": {"headline": {"type": "string"}}}]
            self.article_versions = self.__init_article_versions()

            with open(self.filename, "w+") as file:
                json.dump(self.json_data, file)
            init_app(self.app)

    def tearDown(self):
        super().tearDown()
        if self.filename and os.path.exists(self.filename):
            os.remove(self.filename)

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

            publish_queue.PublishQueueService('publish_queue', superdesk.get_backend()) \
                .delete_by_article_id(self.articles[1]['_id'])
            queue_items = self.app.data.find('publish_queue', None, None)
            self.assertEquals(0, queue_items.count())

    def test_remove_published_expired_content(self):
        with self.app.app_context():
            self.app.data.insert('archive_versions', self.article_versions)

            published_service = get_resource_service('published')
            text_archive = get_resource_service('text_archive')

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

            article_in_legal_archive, article_versions_in_legal_archive, formatted_items, queue_items = \
                self.__get_legal_archive_details(original['item_id'])

            self.assertIsNotNone(article_in_legal_archive, 'Article cannot be none in Legal Archive')

            self.assertGreaterEqual(formatted_items.count(), 1, 'Formatted Items must be greater than or equal to 1')
            for formatted_item in formatted_items:
                self.assertEquals(formatted_item['item_id'], self.articles[0]['_id'])
                self.assertEquals(formatted_item['item_version'], self.articles[0][config.VERSION])

            self.assertGreaterEqual(queue_items.count(), 1, 'Publish Queue Items must be greater than or equal to 1')

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
            killed[config.VERSION] += 1
            get_resource_service('archive_publish').queue_transmission(killed)
            published_service.post([killed])

            published_items = published_service.get_other_published_items(published['item_id'])
            self.assertEquals(2, published_items.count())

            published_service.update_published_items(killed['item_id'], 'expiry', utcnow() + timedelta(minutes=-60))
            RemoveExpiredPublishContent().run()

            published_items = published_service.get_other_published_items(killed['item_id'])
            self.assertEquals(0, published_items.count())

            articles_in_text_archive = text_archive.get(req=None, lookup={'item_id': self.articles[2]['_id']})
            self.assertEquals(articles_in_text_archive.count(), 0)

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

    def test_remove_expired_published_and_killed_content(self):
        cmd = ValidatorsPopulateCommand()

        with self.app.app_context():
            cmd.run(self.filename)
            self.app.data.insert('archive_versions', self.article_versions)

            published_service = get_resource_service('published')
            text_archive = get_resource_service('text_archive')

            # Publishing an Article
            doc = self.articles[0]
            original = doc.copy()
            get_resource_service('archive_publish').queue_transmission(original)
            published_service.post([original])

            published_items = published_service.get_other_published_items(original['item_id'])
            self.assertEquals(1, published_items.count())

            # Setting the expiry date of the published article to 1 hr back from now
            published_service.update_published_items(original['item_id'], 'expiry', utcnow() + timedelta(minutes=-60))

            # Killing the published article and manually inserting the version of the article as unittests use
            # service directly
            _current_version = doc[config.VERSION] + 1
            get_resource_service('archive_kill').patch(id=doc['_id'],
                                                       updates={config.VERSION: _current_version})
            killed_version = {
                'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4f9',
                versioned_id_field(): '1',
                'type': 'text',
                config.VERSION: _current_version,
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
                'subject': [{'qcode': '17004000', 'name': 'Statistics'}, {'qcode': '04001002', 'name': 'Weather'}],
                'state': 'published',
                'expiry': utcnow() + timedelta(minutes=20),
                'unique_name': '#2'
            }
            self.app.data.insert('archive_versions', [killed_version])

            # Executing the Expiry Job for the Published Article and asserting the collections
            RemoveExpiredPublishContent().run()

            articles_in_text_archive = text_archive.get(req=None, lookup={'item_id': original['item_id']})
            self.assertEquals(articles_in_text_archive.count(), 0)

            published_items = published_service.get_other_published_items(str(original['item_id']))
            self.assertEquals(1, published_items.count())

            article_in_production = get_resource_service(ARCHIVE).find_one(req=None, _id=original['item_id'])
            self.assertIsNotNone(article_in_production)
            self.assertEquals(article_in_production['state'], 'killed')
            self.assertEquals(article_in_production[config.VERSION], _current_version)

            # Validate the collections in Legal Archive
            article_in_legal_archive, article_versions_in_legal_archive, formatted_items, queue_items = \
                self.__get_legal_archive_details(original['item_id'])

            self.assertIsNotNone(article_in_legal_archive, 'Article cannot be none in Legal Archive')
            self.assertEquals(article_in_legal_archive['state'], 'published')

            self.assertIsNotNone(article_versions_in_legal_archive, 'Article Versions cannot be none in Legal Archive')
            self.assertEquals(article_versions_in_legal_archive.count(), 4)

            self.assertGreaterEqual(formatted_items.count(), 1, 'Formatted Items must be greater than or equal to 1')
            for formatted_item in formatted_items:
                self.assertEquals(formatted_item['item_id'], original['item_id'])
                self.assertEquals(formatted_item['item_version'], self.articles[0][config.VERSION])

            self.assertGreaterEqual(queue_items.count(), 1, 'Publish Queue Items must be greater than or equal to 1')

            # Setting the expiry date of the killed article to 1 hr back from now and running the job again
            published_service.update_published_items(original['item_id'], 'expiry', utcnow() + timedelta(minutes=-60))
            RemoveExpiredPublishContent().run()

            articles_in_text_archive = text_archive.get(req=None, lookup={'item_id': original['item_id']})
            self.assertEquals(articles_in_text_archive.count(), 0)

            published_items = published_service.get_other_published_items(str(original['item_id']))
            self.assertEquals(0, published_items.count())

            article_in_production = get_resource_service(ARCHIVE).find_one(req=None, _id=original['item_id'])
            self.assertIsNone(article_in_production)

            # Validate the collections in Legal Archive
            article_in_legal_archive, article_versions_in_legal_archive, formatted_items, queue_items = \
                self.__get_legal_archive_details(original['item_id'], article_version=_current_version,
                                                 publishing_action='killed')

            self.assertIsNotNone(article_in_legal_archive, 'Article cannot be none in Legal Archive')
            self.assertEquals(article_in_legal_archive['state'], 'killed')

            self.assertIsNotNone(article_versions_in_legal_archive, 'Article Versions cannot be none in Legal Archive')
            self.assertEquals(article_versions_in_legal_archive.count(), 5)

            self.assertGreaterEqual(formatted_items.count(), 1, 'Formatted Items must be greater than or equal to 1')
            for formatted_item in formatted_items:
                self.assertEquals(formatted_item['item_id'], original['item_id'])
                self.assertEquals(formatted_item['item_version'], _current_version)

            self.assertGreaterEqual(queue_items.count(), 1, 'Publish Queue Items must be greater than or equal to 1')

    def __init_article_versions(self):
        return [{'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4f9',
                 versioned_id_field(): '1',
                 'type': 'text',
                 config.VERSION: 1,
                 'destination_groups': ['4'],
                 'urgency': 4,
                 'pubstatus': 'usable',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'dateline': 'Sydney',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                             {'qcode': '04001002', 'name': 'Weather'}],
                 'state': 'draft',
                 'expiry': utcnow() + timedelta(minutes=20),
                 'unique_name': '#2'},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4f9',
                 versioned_id_field(): '1',
                 'type': 'text',
                 config.VERSION: 2,
                 'destination_groups': ['4'],
                 'urgency': 4,
                 'headline': 'Two students missing',
                 'pubstatus': 'usable',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'dateline': 'Sydney',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                             {'qcode': '04001002', 'name': 'Weather'}],
                 'state': 'submitted',
                 'expiry': utcnow() + timedelta(minutes=20),
                 'unique_name': '#2'},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4f9',
                 versioned_id_field(): '1',
                 'type': 'text',
                 config.VERSION: 3,
                 'destination_groups': ['4'],
                 'urgency': 4,
                 'headline': 'Two students missing',
                 'pubstatus': 'usable',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'ednote': 'Andrew Marwood contributed to this article',
                 'dateline': 'Sydney',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                             {'qcode': '04001002', 'name': 'Weather'}],
                 'state': 'in_progress',
                 'expiry': utcnow() + timedelta(minutes=20),
                 'unique_name': '#2'},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4f9',
                 versioned_id_field(): '1',
                 'type': 'text',
                 config.VERSION: 4,
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
                 'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                             {'qcode': '04001002', 'name': 'Weather'}],
                 'state': 'published',
                 'expiry': utcnow() + timedelta(minutes=20),
                 'unique_name': '#2'}]

    def __get_legal_archive_details(self, article_id, article_version=None, publishing_action=None):
        archive_service = get_resource_service(LEGAL_ARCHIVE_NAME)
        archive_versions_service = get_resource_service(LEGAL_ARCHIVE_VERSIONS_NAME)
        publish_queue_service = get_resource_service(LEGAL_PUBLISH_QUEUE_NAME)
        formatted_items_service = get_resource_service(LEGAL_FORMATTED_ITEM_NAME)

        article = archive_service.find_one(_id=article_id, req=None)
        article_versions = archive_versions_service.get(req=None, lookup={versioned_id_field(): article_id})

        lookup = {'item_id': article_id, 'publishing_action': publishing_action} if publishing_action else \
            {'item_id': article_id}
        queue_items = publish_queue_service.get(req=None, lookup=lookup)

        lookup = {'item_id': article_id, 'item_version': article_version} if article_version else \
            {'item_id': article_id}
        formatted_items = formatted_items_service.get(req=None, lookup=lookup)

        return article, article_versions, formatted_items, queue_items
