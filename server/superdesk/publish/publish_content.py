# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
import superdesk
import logging
from superdesk.celery_app import celery
from superdesk.utc import utcnow
from datetime import datetime
import superdesk.publish
from superdesk.errors import PublishQueueError
from superdesk.celery_task_utils import is_task_running, mark_task_as_not_running

logger = logging.getLogger(__name__)

UPDATE_SCHEDULE_DEFAULT = {'seconds': 10}


class PublishContent(superdesk.Command):
    """Runs deliveries"""

    def run(self, provider_type=None):
        output_channels = superdesk.get_resource_service('output_channels').get(req=None, lookup={'is_active': True})
        output_channels = {str(output_channel['_id']): output_channel for output_channel in output_channels}

        for subscriber in superdesk.get_resource_service('subscribers').get(req=None, lookup={}):
            if subscriber['is_active']:
                for destination in subscriber.get('destinations', []):
                    kwargs = {
                        'subscriber': subscriber,
                        'destination': destination,
                        'output_channels': output_channels
                    }

                    publish.apply_async(
                        expires=10,
                        kwargs=kwargs)


@celery.task(soft_time_limit=1800)
def publish(subscriber, destination, output_channels):
    """
    Fetches items from publish queue as per the configuration,
    calls the transmit function.
    """

    if is_task_running(destination['name'],
                       subscriber[superdesk.config.ID_FIELD],
                       UPDATE_SCHEDULE_DEFAULT):
        return

    try:
        lookup = {'subscriber_id': subscriber.get('_id'),
                  'destination.name': destination.get('name'),
                  'state': 'pending'}

        items = superdesk.get_resource_service('publish_queue').get(req=None, lookup=lookup)
        if items.count() > 0:
            transmit_items(items, subscriber, destination, output_channels)
    finally:
        mark_task_as_not_running(destination['name'],
                                 subscriber[superdesk.config.ID_FIELD])


def transmit_items(queue_items, subscriber, destination, output_channels):
    failed_items = []

    for queue_item in queue_items:
        # Check if output channel is active
        if not (output_channels.get(str(queue_item['output_channel_id']), {})).get('is_active', False):
            continue

        try:
            if not is_on_time(queue_item, destination):
                continue

            # update the status of the item to in-progress
            queue_update = {'state': 'in-progress', 'transmit_started_at': utcnow()}
            superdesk.get_resource_service('publish_queue').patch(queue_item.get('_id'), queue_update)

            # get the formatted item
            formatted_item = superdesk.get_resource_service('formatted_item').\
                find_one(req=None, _id=queue_item['formatted_item_id'])

            transmitter = superdesk.publish.transmitters[destination.get('delivery_type')]
            transmitter.transmit(queue_item, formatted_item, subscriber, destination)
            update_content_state(queue_item)
        except:
            failed_items.append(queue_item)

    if len(failed_items) > 0:
        logger.error('Failed to publish the following items: %s', str(failed_items))


def is_on_time(queue_item, destination):
    """
    Checks if the item is ready to be processed
    :param queue_item: item to be checked
    :return: True if the item is ready
    """
    try:
        if queue_item.get('publish_schedule'):
            publish_schedule = queue_item['publish_schedule']
            if type(publish_schedule) is not datetime:
                raise PublishQueueError.bad_schedule_error(Exception("Schedule is not datetime"),
                                                           destination)
            return utcnow() >= publish_schedule
        return True
    except PublishQueueError:
        raise
    except Exception as ex:
        raise PublishQueueError.bad_schedule_error(ex, destination)


def update_content_state(queue_item):
    """
    Updates the state of the content item to published
    In archive and published repos
    :param queue_item:
    :return:
    """
    if queue_item.get('publish_schedule'):
        try:
            item_update = {'state': 'published'}
            superdesk.get_resource_service('archive').patch(queue_item['item_id'], item_update)
            superdesk.get_resource_service('published').\
                update_published_items(queue_item['item_id'], 'state', 'published')
        except Exception as ex:
            raise PublishQueueError.content_update_error(ex)

superdesk.command('publish:transmit', PublishContent())
