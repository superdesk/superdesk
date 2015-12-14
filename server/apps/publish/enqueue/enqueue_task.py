# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import json
import logging
from superdesk import get_resource_service
import superdesk
from superdesk.celery_app import celery
from superdesk.celery_task_utils import is_task_running, mark_task_as_not_running

from eve.utils import ParsedRequest

from apps.publish.published_item import PUBLISH_STATE, QUEUE_STATE, PUBLISHED
from apps.publish.enqueue import enqueue_item


logger = logging.getLogger(__name__)

UPDATE_SCHEDULE_DEFAULT = {'seconds': 10}


class EnqueueContent(superdesk.Command):
    """Runs deliveries"""

    def run(self, provider_type=None):
        enqueue.apply_async(expires=10)


@celery.task(soft_time_limit=1800)
def enqueue():
    """
    Fetches items from publish queue as per the configuration,
    calls the transmit function.
    """

    if is_task_running("Enqueue", "Articles", UPDATE_SCHEDULE_DEFAULT):
        return

    try:
        items = get_published_items()
        print('ITEMS', [i['_id'] for i in items])

        if items.count() > 0:
            enqueue_items(items)
    finally:
        mark_task_as_not_running("Enqueue", "Articles")


def get_published_items():
    """
    Returns a list of items marked for publishing.
    """
    req = ParsedRequest()
    query = {'query': {'filtered': {'filter': {'term': {QUEUE_STATE: PUBLISH_STATE.PENDING}}}}}
    req.args = {'source': json.dumps(query)}
    return get_resource_service(PUBLISHED).get(req=req, lookup=None)


def enqueue_items(published_items):
    """
    Creates the corresponding entries in the publish queue for each item
    :param list published_items: the list of items marked for publishing
    """
    failed_items = {}

    for queue_item in published_items:
        try:
            enqueue_item(queue_item)
        except Exception as ex:
            logger.exception(ex)
            failed_items[str(queue_item.get('_id'))] = queue_item

    # mark failed items as pending so that Celery tasks will try again
    if len(failed_items) > 0:
        logger.error('Failed to publish the following items: {}'.format(failed_items.keys()))


superdesk.command('publish:enqueue', EnqueueContent())
