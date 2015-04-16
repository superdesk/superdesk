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
import superdesk.publish

logger = logging.getLogger(__name__)


class PublishContent(superdesk.Command):
    """Runs deliveries"""

    def run(self, provider_type=None):
        for subscriber in superdesk.get_resource_service('subscribers').get(req=None, lookup={}):
            if subscriber['is_active']:
                for destination in subscriber.get('destinations', []):
                    kwargs = {
                        'subscriber': subscriber,
                        'destination': destination
                    }

                    publish(subscriber, destination)
                    # publish.apply_async(
                    #     expires=10,
                    #     kwargs=kwargs)


#@celery.task(soft_time_limit=1800)
def publish(subscriber, destination):
    """
    Fetches items from publish queue as per the configuration,
    calls the transmit function.
    """

    lookup = {'subscriber_id': subscriber.get('_id'),
              'destination.name': destination.get('name'),
              'state': 'pending'}

    items = superdesk.get_resource_service('publish_queue').get(req=None, lookup=lookup)
    if items.count() > 0:
        for item in items:
            # update the status of the item to in-progress
            queue_update = {'state': 'in-progress', 'transmit_started_at': utcnow()}
            superdesk.get_resource_service('publish_queue').patch(item.get('_id'), queue_update)

        #start transmission
        transmit_items(items, subscriber, destination)


def transmit_items(items, subscriber, destination):
    failed_items = []

    for item in items:
        try:
            transmitter = superdesk.publish.transmitters[destination.get('delivery_type')]
            transmitter.transmit(item, subscriber, destination)
        except:
            failed_items.append(item)

    if len(failed_items) > 0:
        logger.error('Failed to ingest the following items: %s', str(failed_items))


superdesk.command('publish:transmit', PublishContent())