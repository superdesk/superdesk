# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from unittest import TestCase
from superdesk.utc import utcnow
from datetime import timedelta
from nose.tools import assert_raises
from superdesk.errors import PublishQueueError
from superdesk.publish.publish_content import is_on_time
from superdesk.tests import setup


class UpdateIngestTest(TestCase):
    queue_items = [{"_id": 1,
                    "output_channel_id": 1,
                    "destination": {
                        "delivery_type": "ftp",
                        "config": {
                            "path": "/ipnews",
                            "dest_path": "/",
                            "username": "superdesk-dev1",
                            "password": "Frodo987",
                            "host": "liveftp.aap.com.au",
                            "ip": "144.122.244.55"
                        },
                        "name": "destination1"
                    },
                    "_etag": "f28b9af64f169072fb171ec7f316fc03d5826d6b",
                    "subscriber_id": "552ba73f1d41c8437971613e",
                    "state": "in-progress",
                    "_created": "2015-04-17T13:15:20.000Z",
                    "_updated": "2015-04-20T05:04:25.000Z",
                    "item_id": 1
                    },
                   {
                       "_id": 1,
                       "output_channel_id": 1,
                       "destination": {
                           "delivery_type": "ftp",
                           "config": {
                               "path": "/ipnews",
                               "dest_path": "/",
                               "username": "superdesk-dev1",
                               "password": "Frodo987",
                               "host": "liveftp.aap.com.au",
                               "ip": "144.122.244.55"
                           },
                           "name": "destination1"
                       },
                       "_etag": "f28b9af64f169072fb171ec7f316fc03d5826d6b",
                       "subscriber_id": "552ba73f1d41c8437971613e",
                       "state": "in-progress",
                       "_created": "2015-04-17T13:15:20.000Z",
                       "_updated": "2015-04-20T05:04:25.000Z",
                       "item_id": 1,
                       "publish_schedule": utcnow() + timedelta(minutes=10)},
                   {
                       "_id": 1,
                       "output_channel_id": 1,
                       "destination": {
                           "delivery_type": "ftp",
                           "config": {
                               "path": "/ipnews",
                               "dest_path": "/",
                               "username": "superdesk-dev1",
                               "password": "Frodo987",
                               "host": "liveftp.aap.com.au",
                               "ip": "144.122.244.55"
                           },
                           "name": "destination1"
                       },
                       "_etag": "f28b9af64f169072fb171ec7f316fc03d5826d6b",
                       "subscriber_id": "552ba73f1d41c8437971613e",
                       "state": "in-progress",
                       "_created": "2015-04-17T13:15:20.000Z",
                       "_updated": "2015-04-20T05:04:25.000Z",
                       "item_id": 1,
                       "publish_schedule": "2015-04-20T05:04:25.000Z"}]

    def setUp(self):
        setup(context=self)

    def test_scheduled_items(self):
        self.assertTrue(is_on_time(self.queue_items[0], None))
        self.assertFalse(is_on_time(self.queue_items[1], None))
        with self.app.app_context():
            with assert_raises(PublishQueueError):
                self.assertTrue(is_on_time(self.queue_items[2], None))
