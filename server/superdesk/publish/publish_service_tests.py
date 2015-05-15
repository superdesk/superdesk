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
from nose.tools import assert_raises
from superdesk.errors import PublishQueueError
from apps.publish import init_app
from superdesk.publish.publish_service import PublishService


class PublishServiceTests(TestCase):
    queue_items = [{'_id': '1',
                    'output_channel_id': '1',
                    'destination': {
                        'delivery_type': 'ftp',
                        'config': {},
                        'name': 'destination1'
                    },
                    'subscriber_id': '1',
                    'state': 'in-progress',
                    'item_id': 1
                    }]

    output_channel = [{'_id': '1',
                       'name': 'OC1',
                       'description': 'Testing...',
                       'channel_type': 'metadata',
                       'is_active': True,
                       'format': 'nitf'},
                      {'_id': '2',
                       'name': 'OC1',
                       'description': 'Testing...',
                       'channel_type': 'metadata',
                       'is_active': True,
                       'format': 'nitf',
                       'critical_errors': {'9004': True}}]

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

    def test_close_output_channel_doesnt_close(self):
        with self.app.app_context():
            output_channel = self.app.data.find('output_channels', None, None)[0]
            self.assertTrue(output_channel.get('is_active'))
            PublishService().close_transmitter(output_channel, 'output_channels',
                                               PublishQueueError.bad_schedule_error())
            output_channel = self.app.data.find('output_channels', None, None)[0]
            self.assertTrue(output_channel.get('is_active'))

    def test_close_output_channel_does_close(self):
        with self.app.app_context():
            output_channel = self.app.data.find('output_channels', None, None)[1]
            self.assertTrue(output_channel.get('is_active'))
            PublishService().close_transmitter(output_channel, 'output_channels',
                                               PublishQueueError.bad_schedule_error())
            output_channel = self.app.data.find('output_channels', None, None)[1]
            self.assertFalse(output_channel.get('is_active'))

    def test_close_subscriber_doesnt_close(self):
        with self.app.app_context():
            subscriber = self.app.data.find('subscribers', None, None)[0]
            self.assertTrue(subscriber.get('is_active'))
            PublishService().close_transmitter(subscriber, 'subscribers',
                                               PublishQueueError.destination_group_not_found_error())
            subscriber = self.app.data.find('subscribers', None, None)[0]
            self.assertTrue(subscriber.get('is_active'))
            self.assertIsNone(subscriber.get('last_closed'))

    def test_close_subscriber_does_close(self):
        with self.app.app_context():
            subscriber = self.app.data.find('subscribers', None, None)[0]
            self.assertTrue(subscriber.get('is_active'))
            PublishService().close_transmitter(subscriber, 'subscribers',
                                               PublishQueueError.bad_schedule_error())
            subscriber = self.app.data.find('subscribers', None, None)[0]
            self.assertFalse(subscriber.get('is_active'))
            self.assertIsNotNone(subscriber.get('last_closed'))

    def test_transmit_closes_subscriber(self):
        def mock_transmit(*args):
            raise PublishQueueError.bad_schedule_error()

        with self.app.app_context():
            subscriber = self.app.data.find('subscribers', None, None)[0]
            output_channel = self.app.data.find('output_channels', None, None)[0]
            publish_service = PublishService()
            publish_service._transmit = mock_transmit
            with assert_raises(PublishQueueError):
                publish_service.transmit(self.queue_items[0], None, subscriber, None, output_channel)
            subscriber = self.app.data.find('subscribers', None, None)[0]
            self.assertFalse(subscriber.get('is_active'))
            self.assertIsNotNone(subscriber.get('last_closed'))
            self.assertTrue(output_channel.get('is_active'))
            self.assertIsNone(output_channel.get('last_closed'))
