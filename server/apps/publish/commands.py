# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import logging

from eve.utils import ParsedRequest, date_to_str

from superdesk.celery_app import celery
import superdesk
from superdesk.celery_task_utils import is_task_running, mark_task_as_not_running
from superdesk.utc import utcnow
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE

logger = logging.getLogger(__name__)

UPDATE_SCHEDULE_DEFAULT = {'minutes': 30}


class RemoveExpiredPublishContent(superdesk.Command):
    """
    Remove expired items from published.
    """

    def run(self):
        remove_expired_content.apply_async(expires=1800)


@celery.task(soft_time_limit=1800)
def remove_expired_content():
    """
    Celery Task which removes the expired content from published collection.
    """

    logger.info('Removing expired content from published')

    if is_task_running("publish", "remove_expired", UPDATE_SCHEDULE_DEFAULT):
        return

    try:
        now = date_to_str(utcnow())
        items = get_expired_items(now)

        for item in items:
            logger.info('deleting article of type {} with id {} and headline {} -- expired on: {} now: {}'.
                        format(item['type'], item['_id'], item['headline'], item['expiry'], now))

            superdesk.get_resource_service('published').remove_expired(item)
    finally:
        mark_task_as_not_running("publish", "remove_expired")


def get_expired_items(expired_date_time, limit=100):
    """
    Fetches the expired articles from published collection. Expiry Conditions:
        1.  can_be_removed flag is True
        2.  Item Expiry is less than or equal to expired_date_time, State of the Item is not SCHEDULED and
            allow_post_publish_actions flag is True

    :param expired_date_time:
    :param limit:
    :return: expired articles from published collection
    """

    logger.info('Get expired content from published')
    query = {
        '$or': [
            {'can_be_removed': True},
            {'$and': [
                {'expiry': {'$lte': expired_date_time}},
                {ITEM_STATE: {'$ne': CONTENT_STATE.SCHEDULED}},
                {'allow_post_publish_actions': True}
            ]}
        ]
    }

    req = ParsedRequest()
    req.sort = '_created'
    req.max_results = limit

    return superdesk.get_resource_service('published').get_from_mongo(req=req, lookup=query)

superdesk.command('publish:remove_expired', RemoveExpiredPublishContent())
