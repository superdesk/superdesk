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
from superdesk.utc import utcnow
from datetime import timedelta
from nose.tools import assert_raises
from superdesk.errors import PublishQueueError
from superdesk.publish.publish_content import is_on_time, update_content_state, get_queue_items
from apps.publish import init_app
from superdesk import config


class PublishContentTests(TestCase):
    queue_items = [{"_id": 1,
                    "destination": {
                        "delivery_type": "ftp",
                        "config": {},
                        "name": "destination1"
                    },
                    "_etag": "f28b9af64f169072fb171ec7f316fc03d5826d6b",
                    "subscriber_id": "552ba73f1d41c8437971613e",
                    "state": "pending",
                    "_created": "2015-04-17T13:15:20.000Z",
                    "_updated": "2015-04-20T05:04:25.000Z",
                    "item_id": 1
                    },
                   {
                       "_id": 2,
                       "destination": {
                           "delivery_type": "ftp",
                           "config": {},
                           "name": "destination1"
                       },
                       "_etag": "f28b9af64f169072fb171ec7f316fc03d5826d6b",
                       "subscriber_id": "552ba73f1d41c8437971613e",
                       "state": "pending",
                       "_created": "2015-04-17T13:15:20.000Z",
                       "_updated": "2015-04-20T05:04:25.000Z",
                       "item_id": 1,
                       "publish_schedule": utcnow() + timedelta(minutes=10)},
                   {
                       "_id": 3,
                       "destination": {
                           "delivery_type": "ftp",
                           "config": {},
                           "name": "destination1"
                       },
                       "_etag": "f28b9af64f169072fb171ec7f316fc03d5826d6b",
                       "subscriber_id": "552ba73f1d41c8437971613e",
                       "state": "pending",
                       "_created": "2015-04-17T13:15:20.000Z",
                       "_updated": "2015-04-20T05:04:25.000Z",
                       "item_id": '2',
                       "publish_schedule": "2015-04-20T05:04:25.000Z"},
                   {
                       "_id": 4,
                       "destination": {
                           "delivery_type": "pull",
                           "config": {},
                           "name": "destination1"
                       },
                       "_etag": "f28b9af64f169072fb171ec7f316fc03d5826d6b",
                       "subscriber_id": "552ba73f1d41c8437971613e",
                       "state": "pending",
                       "_created": "2015-04-17T13:15:20.000Z",
                       "_updated": "2015-04-20T05:04:25.000Z",
                       "item_id": '2'}]

    articles = [{'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a974-xy4532fe33f9',
                 '_id': '2',
                 'type': 'text',
                 'last_version': 3,
                 '_etag': '821739912837',
                 'body_html': 'Test body of the second article',
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
                 'publish_schedule': "2016-05-30T10:00:00+0000",
                 'state': 'scheduled',
                 'original_creator': '553cea4d1d41c85d4d42ff98',
                 'task': {'desk': 1}}]

    desks = [{'_id': 1, 'spike_expiry': 20, 'incoming_stage': 1}]
    stages = [{'_id': 1, 'desk': 1}]
    published = [{'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a974-xy4532fe33f9',
                  'item_id': '2',
                  '_id': 333,
                  '_etag': 821739912837,
                  'last_version': 3,
                  'body_html': 'Test body of the second article',
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
                  'publish_schedule': "2016-05-30T10:00:00+0000",
                  'state': 'scheduled'}]

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.app.data.insert('stages', self.stages)
            self.app.data.insert('desks', self.desks)
            self.app.data.insert('archive', self.articles)
            self.app.data.insert('published', self.published)
            init_app(self.app)

    def test_scheduled_items(self):
        self.assertTrue(is_on_time(self.queue_items[0]))
        self.assertFalse(is_on_time(self.queue_items[1]))
        with self.app.app_context():
            with assert_raises(PublishQueueError):
                self.assertTrue(is_on_time(self.queue_items[2]))

    def test_update_content_state(self):
        with self.app.app_context():
            published_items = self.app.data.find('published', None, None)
            archive_items = self.app.data.find_all('archive', None)
            self.assertEquals(1, published_items.count())
            self.assertEquals(1, archive_items.count())
            self.assertEquals(published_items[0]['state'], 'scheduled')
            self.assertEquals(archive_items[0]['state'], 'scheduled')
            update_content_state(self.queue_items[2])
            published_items = self.app.data.find('published', None, None)
            archive_items = self.app.data.find_all('archive', None)
            self.assertEquals(1, published_items.count())
            self.assertEquals(1, archive_items.count())
            self.assertEquals(published_items[0]['state'], 'published')
            self.assertEquals(archive_items[0]['state'], 'published')

    def test_queue_items(self):
        with self.app.app_context():
            self.app.data.insert('publish_queue', self.queue_items)
            items = get_queue_items()
            self.assertEqual(3, items.count())
            ids = [item[config.ID_FIELD] for item in items]
            self.assertNotIn(4, ids)
