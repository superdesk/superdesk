# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.publish import SUBSCRIBER_TYPES

from test_factory import SuperdeskTestCase
from nose.tools import assert_raises
from superdesk.errors import PublishQueueError
from apps.publish import init_app
from superdesk.publish.publish_service import PublishService


class PublishServiceTests(SuperdeskTestCase):
    queue_items = [{"_id": "1",
                    "destination": {"name": "NITF", "delivery_type": "ftp", "format": "nitf", "config": {}},
                    "subscriber_id": "1",
                    "state": "in-progress",
                    "item_id": 1
                    }]

    subscribers = [{"_id": "1", "name": "Test", "subscriber_type": SUBSCRIBER_TYPES.WIRE, "media_type": "media",
                    "is_active": True, "sequence_num_settings": {"max": 10, "min": 1},
                    "critical_errors": {"9004": True},
                    "destinations": [{"name": "NITF", "delivery_type": "ftp", "format": "nitf", "config": {}}]
                    }]

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.app.data.insert('subscribers', self.subscribers)
            self.app.data.insert('publish_queue', self.queue_items)

            init_app(self.app)

    def test_close_subscriber_doesnt_close(self):
        with self.app.app_context():
            subscriber = self.app.data.find('subscribers', None, None)[0]
            self.assertTrue(subscriber.get('is_active'))

            PublishService().close_transmitter(subscriber, PublishQueueError.unknown_format_error())
            subscriber = self.app.data.find('subscribers', None, None)[0]
            self.assertTrue(subscriber.get('is_active'))

    def test_close_subscriber_does_close(self):
        with self.app.app_context():
            subscriber = self.app.data.find('subscribers', None, None)[0]
            self.assertTrue(subscriber.get('is_active'))

            PublishService().close_transmitter(subscriber, PublishQueueError.bad_schedule_error())
            subscriber = self.app.data.find('subscribers', None, None)[0]
            self.assertFalse(subscriber.get('is_active'))

    def test_transmit_closes_subscriber(self):
        def mock_transmit(*args):
            raise PublishQueueError.bad_schedule_error()

        with self.app.app_context():
            subscriber = self.app.data.find('subscribers', None, None)[0]

            publish_service = PublishService()
            publish_service._transmit = mock_transmit

            with assert_raises(PublishQueueError):
                publish_service.transmit(self.queue_items[0])

            subscriber = self.app.data.find('subscribers', None, None)[0]
            self.assertFalse(subscriber.get('is_active'))
            self.assertIsNotNone(subscriber.get('last_closed'))
