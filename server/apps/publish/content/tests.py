# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from copy import copy
from datetime import timedelta
import os
import json

from eve.utils import config, ParsedRequest
from eve.versioning import versioned_id_field

from apps.packages.package_service import PackageService
from apps.publish.content.publish import ArchivePublishService
from superdesk.publish.subscribers import SUBSCRIBER_TYPES
from apps.validators import ValidatorsPopulateCommand
from superdesk.metadata.packages import RESIDREF
from test_factory import SuperdeskTestCase
from superdesk.publish import init_app, publish_queue
from superdesk.utc import utcnow
from superdesk import get_resource_service
import superdesk
from apps.archive.archive import SOURCE as ARCHIVE
from superdesk.metadata.item import TAKES_PACKAGE, PACKAGE_TYPE, ITEM_STATE, CONTENT_STATE, ITEM_TYPE, CONTENT_TYPE
from apps.publish.published_item import LAST_PUBLISHED_VERSION

ARCHIVE_PUBLISH = 'archive_publish'
ARCHIVE_CORRECT = 'archive_correct'
ARCHIVE_KILL = 'archive_kill'

PUBLISH_QUEUE = 'publish_queue'
PUBLISHED = 'published'


class ArchivePublishTestCase(SuperdeskTestCase):
    def init_data(self):
        self.subscribers = [{"_id": "1", "name": "sub1", "is_active": True, "subscriber_type": SUBSCRIBER_TYPES.WIRE,
                             "media_type": "media", "sequence_num_settings": {"max": 10, "min": 1},
                             "email": "test@test.com",
                             "destinations": [{"name": "dest1", "format": "nitf",
                                               "delivery_type": "ftp",
                                               "config": {"address": "127.0.0.1", "username": "test"}
                                               }]
                             },
                            {"_id": "2", "name": "sub2", "is_active": True, "subscriber_type": SUBSCRIBER_TYPES.WIRE,
                             "media_type": "media", "sequence_num_settings": {"max": 10, "min": 1},
                             "email": "test@test.com",
                             "destinations": [{"name": "dest2", "format": "AAP ANPA", "delivery_type": "filecopy",
                                               "config": {"address": "/share/copy"}
                                               },
                                              {"name": "dest3", "format": "AAP ANPA", "delivery_type": "Email",
                                               "config": {"recipients": "test@sourcefabric.org"}
                                               }]
                             },
                            {"_id": "3", "name": "sub3", "is_active": True, "subscriber_type": SUBSCRIBER_TYPES.DIGITAL,
                             "media_type": "media", "sequence_num_settings": {"max": 10, "min": 1},
                             "email": "test@test.com",
                             "destinations": [{"name": "dest1", "format": "nitf",
                                               "delivery_type": "ftp",
                                               "config": {"address": "127.0.0.1", "username": "test"}
                                               }]
                             },
                            {"_id": "4", "name": "sub4", "is_active": True, "subscriber_type": SUBSCRIBER_TYPES.WIRE,
                             "media_type": "media", "sequence_num_settings": {"max": 10, "min": 1},
                             "geo_restrictions": "New South Wales", "email": "test@test.com",
                             "destinations": [{"name": "dest1", "format": "nitf",
                                               "delivery_type": "ftp",
                                               "config": {"address": "127.0.0.1", "username": "test"}
                                               }]
                             },
                            {"_id": "5", "name": "sub5", "is_active": True, "subscriber_type": SUBSCRIBER_TYPES.ALL,
                             "media_type": "media", "sequence_num_settings": {"max": 10, "min": 1},
                             "email": "test@test.com",
                             "destinations": [{"name": "dest1", "format": "ninjs",
                                               "delivery_type": "ftp",
                                               "config": {"address": "127.0.0.1", "username": "test"}
                                               }]
                             }]

        self.articles = [{'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4f9',
                          '_id': '1',
                          ITEM_TYPE: CONTENT_TYPE.TEXT,
                          'last_version': 3,
                          config.VERSION: 4,
                          'body_html': 'Test body',
                          'anpa_category': [{'qcode': 'A', 'name': 'Sport'}],
                          'urgency': 4,
                          'headline': 'Two students missing',
                          'pubstatus': 'usable',
                          'firstcreated': utcnow(),
                          'byline': 'By Alan Karben',
                          'ednote': 'Andrew Marwood contributed to this article',
                          'dateline': {'located': {'city': 'Sydney'}},
                          'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          ITEM_STATE: CONTENT_STATE.PUBLISHED,
                          'expiry': utcnow() + timedelta(minutes=20),
                          'unique_name': '#1'},
                         {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a974-xy4532fe33f9',
                          '_id': '2',
                          'last_version': 3,
                          config.VERSION: 4,
                          'body_html': 'Test body of the second article',
                          'urgency': 4,
                          'anpa_category': [{'qcode': 'A', 'name': 'Sport'}],
                          'headline': 'Another two students missing',
                          'pubstatus': 'usable',
                          'firstcreated': utcnow(),
                          'byline': 'By Alan Karben',
                          'ednote': 'Andrew Marwood contributed to this article',
                          'dateline': {'located': {'city': 'Sydney'}},
                          'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          'expiry': utcnow() + timedelta(minutes=20),
                          ITEM_STATE: CONTENT_STATE.PROGRESS,
                          'publish_schedule': "2016-05-30T10:00:00+0000",
                          ITEM_TYPE: CONTENT_TYPE.TEXT,
                          'unique_name': '#2'},
                         {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4fa',
                          '_id': '3',
                          'last_version': 3,
                          config.VERSION: 4,
                          'body_html': 'Test body',
                          'urgency': 4,
                          'anpa_category': [{'qcode': 'A', 'name': 'Sport'}],
                          'headline': 'Two students missing killed',
                          'pubstatus': 'usable',
                          'firstcreated': utcnow(),
                          'byline': 'By Alan Karben',
                          'ednote': 'Andrew Marwood contributed to this article killed',
                          'dateline': {'located': {'city': 'Sydney'}},
                          'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          ITEM_STATE: CONTENT_STATE.KILLED,
                          'expiry': utcnow() + timedelta(minutes=20),
                          ITEM_TYPE: CONTENT_TYPE.TEXT,
                          'unique_name': '#3'},
                         {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4fb',
                          '_id': '4',
                          'last_version': 3,
                          config.VERSION: 4,
                          'body_html': 'Take-1 body',
                          'urgency': 4,
                          'headline': 'Take-1 headline',
                          'abstract': 'Abstract for take-1',
                          'anpa_category': [{'qcode': 'A', 'name': 'Sport'}],
                          'pubstatus': 'done',
                          'firstcreated': utcnow(),
                          'byline': 'By Alan Karben',
                          'dateline': {'located': {'city': 'Sydney'}},
                          'slugline': 'taking takes',
                          'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          ITEM_STATE: CONTENT_STATE.PROGRESS,
                          'expiry': utcnow() + timedelta(minutes=20),
                          ITEM_TYPE: CONTENT_TYPE.TEXT,
                          'linked_in_packages': [{"package": "7", "package_type": "takes"}],
                          'unique_name': '#4'},
                         {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4fg',
                          '_id': '5',
                          'last_version': 3,
                          config.VERSION: 4,
                          'body_html': 'Take-2 body',
                          'urgency': 4,
                          'headline': 'Take-2 headline',
                          'abstract': 'Abstract for take-1',
                          'anpa_category': [{'qcode': 'A', 'name': 'Sport'}],
                          'pubstatus': 'done',
                          'firstcreated': utcnow(),
                          'byline': 'By Alan Karben',
                          'dateline': {'located': {'city': 'Sydney'}},
                          'slugline': 'taking takes',
                          'linked_in_packages': [{"package": "7", "package_type": "takes"}],
                          'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          ITEM_STATE: CONTENT_STATE.PROGRESS,
                          'expiry': utcnow() + timedelta(minutes=20),
                          ITEM_TYPE: CONTENT_TYPE.TEXT,
                          'unique_name': '#5'},
                         {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4fc',
                          '_id': '6',
                          'last_version': 2,
                          config.VERSION: 3,
                          ITEM_TYPE: CONTENT_TYPE.COMPOSITE,
                          'groups': [{'id': 'root', 'refs': [{'idRef': 'main'}], 'role': 'grpRole:NEP'},
                                     {
                                         'id': 'main',
                                         'refs': [
                                             {
                                                 'location': ARCHIVE,
                                                 'guid': '5',
                                                 ITEM_TYPE: CONTENT_TYPE.TEXT,
                                                 RESIDREF: '5'
                                             },
                                             {
                                                 'location': ARCHIVE,
                                                 'guid': '4',
                                                 ITEM_TYPE: CONTENT_TYPE.TEXT,
                                                 RESIDREF: '4'
                                             }
                                         ],
                                         'role': 'grpRole:main'}],
                          'firstcreated': utcnow(),
                          'expiry': utcnow() + timedelta(minutes=20),
                          'unique_name': '#6',
                          ITEM_STATE: CONTENT_STATE.PROGRESS},
                         {'guid': 'tag:localhost:2015:ab-69b961-2816-4b8a-a584-a7b402fed4fc',
                          '_id': '7',
                          'last_version': 2,
                          config.VERSION: 3,
                          ITEM_TYPE: CONTENT_TYPE.COMPOSITE,
                          'package_type': 'takes',
                          'groups': [{'id': 'root', 'refs': [{'idRef': 'main'}], 'role': 'grpRole:NEP'},
                                     {
                                         'id': 'main',
                                         'refs': [
                                             {
                                                 'location': ARCHIVE,
                                                 'guid': '5',
                                                 'sequence': 1,
                                                 ITEM_TYPE: CONTENT_TYPE.TEXT
                                             },
                                             {
                                                 'location': ARCHIVE,
                                                 'guid': '4',
                                                 'sequence': 2,
                                                 ITEM_TYPE: CONTENT_TYPE.TEXT
                                             }
                                         ],
                                         'role': 'grpRole:main'}],
                          'firstcreated': utcnow(),
                          'expiry': utcnow() + timedelta(minutes=20),
                          'sequence': 2,
                          'state': 'draft',
                          'unique_name': '#7'},
                         {'guid': '8',
                          '_id': '8',
                          'last_version': 3,
                          config.VERSION: 4,
                          'targeted_for': [{'name': 'New South Wales', 'allow': True}],
                          'body_html': 'Take-1 body',
                          'urgency': 4,
                          'headline': 'Take-1 headline',
                          'abstract': 'Abstract for take-1',
                          'anpa_category': [{'qcode': 'A', 'name': 'Sport'}],
                          'pubstatus': 'done',
                          'firstcreated': utcnow(),
                          'byline': 'By Alan Karben',
                          'dateline': {'located': {'city': 'Sydney'}},
                          'slugline': 'taking takes',
                          'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          ITEM_STATE: CONTENT_STATE.PROGRESS,
                          'expiry': utcnow() + timedelta(minutes=20),
                          ITEM_TYPE: CONTENT_TYPE.TEXT,
                          'unique_name': '#8'},
                         {'_id': '9', 'urgency': 3, 'headline': 'creator', ITEM_STATE: CONTENT_STATE.FETCHED},
                         {'guid': 'tag:localhost:2015:69b961ab-a7b402fed4fb',
                          'last_version': 3,
                          config.VERSION: 4,
                          'body_html': 'Student Crime. Police Missing.',
                          'urgency': 4,
                          'headline': 'Police Missing',
                          'abstract': 'Police Missing',
                          'anpa_category': [{'qcode': 'A', 'name': 'Australian General News'}],
                          'pubstatus': 'usable',
                          'firstcreated': utcnow(),
                          'byline': 'By Alan Karben',
                          'dateline': {'located': {'city': 'Sydney'}},
                          'slugline': 'Police Missing',
                          'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          ITEM_STATE: CONTENT_STATE.PROGRESS,
                          ITEM_TYPE: CONTENT_TYPE.TEXT,
                          'unique_name': '#9'},
                         {'guid': 'tag:localhost:10:10:10:2015:69b961ab-2816-4b8a-a584-a7b402fed4fc',
                          '_id': '100',
                          config.VERSION: 3,
                          ITEM_TYPE: CONTENT_TYPE.COMPOSITE,
                          'groups': [{'id': 'root', 'refs': [{'idRef': 'main'}], 'role': 'grpRole:NEP'},
                                     {'id': 'main',
                                      'refs': [{'location': ARCHIVE, ITEM_TYPE: CONTENT_TYPE.COMPOSITE, RESIDREF: '6'}],
                                      'role': 'grpRole:main'}],
                          'firstcreated': utcnow(),
                          'expiry': utcnow() + timedelta(minutes=20),
                          'unique_name': '#100',
                          ITEM_STATE: CONTENT_STATE.PROGRESS}]

    def setUp(self):
        super().setUp()
        self.init_data()

        self.app.data.insert('subscribers', self.subscribers)
        self.app.data.insert(ARCHIVE, self.articles)

        self.filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), "validators.json")
        self.json_data = [
            {"_id": "kill_text", "act": "kill", "type": "text", "schema": {"headline": {"type": "string"}}},
            {"_id": "publish_text", "act": "publish", "type": "text", "schema": {}},
            {"_id": "correct_text", "act": "correct", "type": "text", "schema": {}},
            {"_id": "publish_composite", "act": "publish", "type": "composite", "schema": {}},
        ]
        self.article_versions = self._init_article_versions()

        with open(self.filename, "w+") as file:
            json.dump(self.json_data, file)
        init_app(self.app)
        ValidatorsPopulateCommand().run(self.filename)

    def tearDown(self):
        super().tearDown()
        if self.filename and os.path.exists(self.filename):
            os.remove(self.filename)

    def _init_article_versions(self):
        resource_def = self.app.config['DOMAIN']['archive_versions']
        version_id = versioned_id_field(resource_def)
        return [{'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4f9',
                 version_id: '1',
                 ITEM_TYPE: CONTENT_TYPE.TEXT,
                 config.VERSION: 1,
                 'urgency': 4,
                 'pubstatus': 'usable',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'dateline': {'located': {'city': 'Sydney'}},
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                             {'qcode': '04001002', 'name': 'Weather'}],
                 ITEM_STATE: CONTENT_STATE.DRAFT,
                 'expiry': utcnow() + timedelta(minutes=20),
                 'unique_name': '#8'},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4f9',
                 version_id: '1',
                 ITEM_TYPE: CONTENT_TYPE.TEXT,
                 config.VERSION: 2,
                 'urgency': 4,
                 'headline': 'Two students missing',
                 'pubstatus': 'usable',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'dateline': {'located': {'city': 'Sydney'}},
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                             {'qcode': '04001002', 'name': 'Weather'}],
                 ITEM_STATE: CONTENT_STATE.SUBMITTED,
                 'expiry': utcnow() + timedelta(minutes=20),
                 'unique_name': '#8'},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4f9',
                 version_id: '1',
                 ITEM_TYPE: CONTENT_TYPE.TEXT,
                 config.VERSION: 3,
                 'urgency': 4,
                 'headline': 'Two students missing',
                 'pubstatus': 'usable',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'ednote': 'Andrew Marwood contributed to this article',
                 'dateline': {'located': {'city': 'Sydney'}},
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                             {'qcode': '04001002', 'name': 'Weather'}],
                 ITEM_STATE: CONTENT_STATE.PROGRESS,
                 'expiry': utcnow() + timedelta(minutes=20),
                 'unique_name': '#8'},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4f9',
                 version_id: '1',
                 ITEM_TYPE: CONTENT_TYPE.TEXT,
                 config.VERSION: 4,
                 'body_html': 'Test body',
                 'urgency': 4,
                 'headline': 'Two students missing',
                 'pubstatus': 'usable',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'ednote': 'Andrew Marwood contributed to this article',
                 'dateline': {'located': {'city': 'Sydney'}},
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                             {'qcode': '04001002', 'name': 'Weather'}],
                 ITEM_STATE: CONTENT_STATE.PROGRESS,
                 'expiry': utcnow() + timedelta(minutes=20),
                 'unique_name': '#8'}]

    def _is_publish_queue_empty(self):
        queue_items = self.app.data.find(PUBLISH_QUEUE, None, None)
        self.assertEqual(0, queue_items.count())

    def _add_content_filters(self, subscriber, is_global=False):
        subscriber['content_filter'] = {'filter_id': 1, 'filter_type': 'blocking'}
        self.app.data.insert('filter_conditions',
                             [{'_id': 1,
                               'field': 'headline',
                               'operator': 'like',
                               'value': 'tor',
                               'name': 'test-1'}])
        self.app.data.insert('filter_conditions',
                             [{'_id': 2,
                               'field': 'urgency',
                               'operator': 'in',
                               'value': '2',
                               'name': 'test-2'}])
        self.app.data.insert('filter_conditions',
                             [{'_id': 3,
                               'field': 'headline',
                               'operator': 'endswith',
                               'value': 'tor',
                               'name': 'test-3'}])
        self.app.data.insert('filter_conditions',
                             [{'_id': 4,
                               'field': 'urgency',
                               'operator': 'in',
                               'value': '2,3,4',
                               'name': 'test-4'}])

        get_resource_service('content_filters').post([{'_id': 1, 'name': 'pf-1', 'is_global': is_global,
                                                       'content_filter': [{"expression": {"fc": [4, 3]}},
                                                                          {"expression": {"fc": [1, 2]}}]
                                                       }])

    def test_publish(self):
        doc = self.articles[3].copy()
        get_resource_service(ARCHIVE_PUBLISH).patch(id=doc['_id'], updates={ITEM_STATE: CONTENT_STATE.PUBLISHED})
        published_doc = get_resource_service(ARCHIVE).find_one(req=None, _id=doc['_id'])
        self.assertIsNotNone(published_doc)
        self.assertEqual(published_doc[config.VERSION], doc[config.VERSION] + 1)
        self.assertEqual(published_doc[ITEM_STATE], ArchivePublishService().published_state)

    def test_versions_across_collections_after_publish(self):
        self.app.data.insert('archive_versions', self.article_versions)

        # Publishing an Article
        doc = self.articles[7]
        original = doc.copy()

        published_version_number = original[config.VERSION] + 1
        get_resource_service(ARCHIVE_PUBLISH).patch(id=doc[config.ID_FIELD],
                                                    updates={ITEM_STATE: CONTENT_STATE.PUBLISHED,
                                                             config.VERSION: published_version_number})

        article_in_production = get_resource_service(ARCHIVE).find_one(req=None, _id=original[config.ID_FIELD])
        self.assertIsNotNone(article_in_production)
        self.assertEqual(article_in_production[ITEM_STATE], CONTENT_STATE.PUBLISHED)
        self.assertEqual(article_in_production[config.VERSION], published_version_number)

        lookup = {'item_id': original[config.ID_FIELD], 'item_version': published_version_number}
        queue_items = list(get_resource_service(PUBLISH_QUEUE).get(req=None, lookup=lookup))
        assert len(queue_items) > 0, \
            "Transmission Details are empty for published item %s" % original[config.ID_FIELD]

        lookup = {'item_id': original[config.ID_FIELD], config.VERSION: published_version_number}
        items_in_published_collection = list(get_resource_service(PUBLISHED).get(req=None, lookup=lookup))
        assert len(items_in_published_collection) > 0, \
            "Item not found in published collection %s" % original[config.ID_FIELD]

    def test_queue_transmission(self):
        self._is_publish_queue_empty()

        doc = copy(self.articles[9])
        schedule_date = utcnow() + timedelta(hours=2)
        get_resource_service(ARCHIVE).patch(id=doc['_id'], updates={'publish_schedule': schedule_date, 'task': {}})
        get_resource_service(ARCHIVE_PUBLISH).patch(id=doc['_id'], updates={ITEM_STATE: CONTENT_STATE.SCHEDULED,
                                                                            'task': {}})
        queue_items = self.app.data.find(PUBLISH_QUEUE, None, None)
        self.assertEqual(7, queue_items.count())

        for item in queue_items:
            self.assertEqual(schedule_date, item["publish_schedule"])

    def test_queue_transmission_for_digital_channels(self):
        self._is_publish_queue_empty()

        archive_publish = get_resource_service(ARCHIVE_PUBLISH)
        doc = copy(self.articles[1])
        subscribers, subscribers_yet_to_receive = archive_publish.get_subscribers(doc, SUBSCRIBER_TYPES.DIGITAL)
        archive_publish.queue_transmission(doc, subscribers)

        queue_items = self.app.data.find(PUBLISH_QUEUE, None, None)
        self.assertEqual(2, queue_items.count())
        self.assertEqual('3', queue_items[0]["subscriber_id"])

    def test_queue_transmission_for_wire_channels(self):
        self._is_publish_queue_empty()

        archive_publish = get_resource_service(ARCHIVE_PUBLISH)
        doc = copy(self.articles[1])
        subscribers, subscribers_yet_to_receive = archive_publish.get_subscribers(doc, SUBSCRIBER_TYPES.WIRE)
        archive_publish.queue_transmission(doc, subscribers)
        queue_items = self.app.data.find(PUBLISH_QUEUE, None, None)

        self.assertEqual(5, queue_items.count())
        expected_subscribers = ['1', '2', '5']
        self.assertIn(queue_items[0]["subscriber_id"], expected_subscribers)
        self.assertIn(queue_items[1]["subscriber_id"], expected_subscribers)
        self.assertIn(queue_items[2]["subscriber_id"], expected_subscribers)

    def test_queue_transmission_wrong_article_type_fails(self):
        self._is_publish_queue_empty()

        doc = copy(self.articles[0])
        doc[ITEM_TYPE] = CONTENT_TYPE.PICTURE

        archive_publish = get_resource_service(ARCHIVE_PUBLISH)
        subscribers, subscribers_yet_to_receive = archive_publish.get_subscribers(doc, SUBSCRIBER_TYPES.DIGITAL)
        no_formatters, queued = archive_publish.queue_transmission(doc, subscribers)
        queue_items = self.app.data.find(PUBLISH_QUEUE, None, None)
        self.assertEqual(1, queue_items.count())
        self.assertEqual(1, len(no_formatters))
        self.assertTrue(queued)

        subscribers, subscribers_yet_to_receive = archive_publish.get_subscribers(doc, SUBSCRIBER_TYPES.WIRE)
        no_formatters, queued = archive_publish.queue_transmission(doc, subscribers)
        queue_items = self.app.data.find(PUBLISH_QUEUE, None, None)
        self.assertEqual(2, queue_items.count())
        self.assertEqual(0, len(no_formatters))
        self.assertTrue(queued)

    def test_delete_from_queue_by_article_id(self):
        self._is_publish_queue_empty()

        doc = copy(self.articles[7])

        archive_publish = get_resource_service(ARCHIVE_PUBLISH)
        archive_publish.patch(id=doc['_id'], updates={ITEM_STATE: CONTENT_STATE.PUBLISHED})

        queue_items = self.app.data.find(PUBLISH_QUEUE, None, None)
        self.assertEqual(4, queue_items.count())

        # this will delete queue transmission for the wire article not the takes package.
        publish_queue.PublishQueueService(PUBLISH_QUEUE, superdesk.get_backend()).delete_by_article_id(doc['_id'])
        self._is_publish_queue_empty()

    def test_can_publish_article(self):
        subscriber = self.subscribers[0]
        self._add_content_filters(subscriber, is_global=False)

        archive_publish_service = get_resource_service(ARCHIVE_PUBLISH)
        can_it = archive_publish_service.conforms_content_filter(subscriber, self.articles[8])
        self.assertFalse(can_it)
        subscriber['content_filter']['filter_type'] = 'permitting'

        can_it = archive_publish_service.conforms_content_filter(subscriber, self.articles[8])
        self.assertTrue(can_it)
        subscriber.pop('content_filter')

    def test_can_publish_article_with_global_filters(self):
        subscriber = self.subscribers[0]
        self._add_content_filters(subscriber, is_global=True)

        service = get_resource_service('content_filters')
        req = ParsedRequest()
        req.args = {'is_global': True}
        global_filters = service.get(req=req, lookup=None)

        publish_service = get_resource_service(ARCHIVE_PUBLISH)
        can_it = publish_service.conforms_global_filter(subscriber, global_filters, self.articles[8])
        self.assertFalse(can_it)

        subscriber['global_filters'] = {'1': False}
        can_it = publish_service.conforms_global_filter(subscriber, global_filters, self.articles[8])
        self.assertTrue(can_it)

        subscriber.pop('content_filter')

    def test_targeted_for_excludes_digital_subscribers(self):
        ValidatorsPopulateCommand().run(self.filename)
        updates = {'targeted_for': [{'name': 'New South Wales', 'allow': True}]}
        doc_id = self.articles[9][config.ID_FIELD]
        get_resource_service(ARCHIVE).patch(id=doc_id, updates=updates)

        get_resource_service(ARCHIVE_PUBLISH).patch(id=doc_id, updates={ITEM_STATE: CONTENT_STATE.PUBLISHED})

        queue_items = self.app.data.find(PUBLISH_QUEUE, None, None)
        self.assertEqual(4, queue_items.count())
        expected_subscribers = ['1', '2']
        self.assertIn(queue_items[0]["subscriber_id"], expected_subscribers)
        self.assertIn(queue_items[1]["subscriber_id"], expected_subscribers)
        self.assertIn(queue_items[2]["subscriber_id"], expected_subscribers)

    def test_maintain_latest_version_for_published(self):
        def get_publish_items(item_id, last_version):
            query = {'query': {'filtered': {'filter': {'and': [
                    {'term': {'item_id': item_id}}, {'term': {LAST_PUBLISHED_VERSION: last_version}}
            ]}}}}
            request = ParsedRequest()
            request.args = {'source': json.dumps(query)}
            return self.app.data.find(PUBLISHED, req=request, lookup=None)

        ValidatorsPopulateCommand().run(self.filename)
        get_resource_service(ARCHIVE).patch(id=self.articles[1][config.ID_FIELD],
                                            updates={'publish_schedule': None, 'task': {}})

        doc = get_resource_service(ARCHIVE).find_one(req=None, _id=self.articles[1][config.ID_FIELD])
        get_resource_service(ARCHIVE_PUBLISH).patch(id=doc[config.ID_FIELD],
                                                    updates={ITEM_STATE: CONTENT_STATE.PUBLISHED})

        queue_items = self.app.data.find(PUBLISH_QUEUE, None, None)
        self.assertEqual(7, queue_items.count())
        published_items = self.app.data.find(PUBLISHED, None, None)
        self.assertEqual(2, published_items.count())
        published_digital_doc = next((item for item in published_items
                                      if item.get(PACKAGE_TYPE) == TAKES_PACKAGE), None)
        published_doc = next((item for item in published_items
                              if item.get('item_id') == doc[config.ID_FIELD]), None)
        self.assertEqual(published_doc[LAST_PUBLISHED_VERSION], True)
        self.assertEqual(published_digital_doc[LAST_PUBLISHED_VERSION], True)

        get_resource_service(ARCHIVE_CORRECT).patch(id=doc[config.ID_FIELD],
                                                    updates={ITEM_STATE: CONTENT_STATE.CORRECTED})
        queue_items = self.app.data.find(PUBLISH_QUEUE, None, None)
        self.assertEqual(14, queue_items.count())
        published_items = self.app.data.find(PUBLISHED, None, None)
        self.assertEqual(4, published_items.count())
        last_published_digital = get_publish_items(published_digital_doc['item_id'], True)
        self.assertEqual(1, last_published_digital.count())
        last_published = get_publish_items(published_doc['item_id'], True)
        self.assertEqual(1, last_published.count())

    def test_added_removed_in_a_package(self):
        package = {"groups": [{"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                              {"id": "main", "refs": [
                                  {
                                      "renditions": {},
                                      "slugline": "Boat",
                                      "guid": "123",
                                      "headline": "item-1 headline",
                                      "location": "archive",
                                      "type": "text",
                                      "itemClass": "icls:text",
                                      "residRef": "123"
                                  },
                                  {
                                      "renditions": {},
                                      "slugline": "Boat",
                                      "guid": "456",
                                      "headline": "item-2 headline",
                                      "location": "archive",
                                      "type": "text",
                                      "itemClass": "icls:text",
                                      "residRef": "456"
                                  },
                                  {
                                      "renditions": {},
                                      "slugline": "Boat",
                                      "guid": "789",
                                      "headline": "item-3 headline",
                                      "location": "archive",
                                      "type": "text",
                                      "itemClass": "icls:text",
                                      "residRef": "789"
                                  }], "role": "grpRole:main"}],
                   "task": {
                       "user": "#CONTEXT_USER_ID#",
                       "status": "todo",
                       "stage": "#desks.incoming_stage#",
                       "desk": "#desks._id#"},
                   "guid": "compositeitem",
                   "headline": "test package",
                   "state": "submitted",
                   "type": "composite"}

        updates = {"groups": [{"id": "root", "refs": [{"idRef": "main"}], "role": "grpRole:NEP"},
                              {"id": "main", "refs": [
                                  {
                                      "renditions": {},
                                      "slugline": "Boat",
                                      "guid": "123",
                                      "headline": "item-1 headline",
                                      "location": "archive",
                                      "type": "text",
                                      "itemClass": "icls:text",
                                      "residRef": "123"
                                  },
                                  {
                                      "renditions": {},
                                      "slugline": "Boat",
                                      "guid": "555",
                                      "headline": "item-2 headline",
                                      "location": "archive",
                                      "type": "text",
                                      "itemClass": "icls:text",
                                      "residRef": "555"
                                  },
                                  {
                                      "renditions": {},
                                      "slugline": "Boat",
                                      "guid": "456",
                                      "headline": "item-2 headline",
                                      "location": "archive",
                                      "type": "text",
                                      "itemClass": "icls:text",
                                      "residRef": "456"
                                  }], "role": "grpRole:main"}],
                   "task": {
                       "user": "#CONTEXT_USER_ID#",
                       "status": "todo",
                       "stage": "#desks.incoming_stage#",
                       "desk": "#desks._id#"},
                   "guid": "compositeitem",
                   "headline": "test package",
                   "state": "submitted",
                   "type": "composite"}

        items = PackageService().get_residrefs(package)
        removed_items, added_items = ArchivePublishService()._get_changed_items(items, updates)
        self.assertEqual(len(removed_items), 1)
        self.assertEqual(len(added_items), 1)
