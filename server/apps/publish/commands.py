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

from eve.utils import ParsedRequest, date_to_str, config
import superdesk
from superdesk.celery_task_utils import is_task_running, mark_task_as_not_running
from superdesk.utc import utcnow
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE, ITEM_TYPE
from apps.archive.commands import get_overdue_scheduled_items

logger = logging.getLogger(__name__)

REMOVE_SPIKE_DEFAULT = {'minutes': 30}
UPDATE_OVERDUE_SCHEDULED_DEFAULT = {'minutes': 10}


class RemoveExpiredPublishContent(superdesk.Command):
    """
    Remove expired items from published.
    """

    def run(self):
        self.remove_expired_content()

    def remove_expired_content(self):
        """
        Removes the expired content from published collection.
        """

        logger.info('Removing expired content from published')

        if is_task_running("publish", "remove_expired", REMOVE_SPIKE_DEFAULT):
            return

        try:
            self.remove_expired_items()
        finally:
            mark_task_as_not_running("publish", "remove_expired")

    def remove_expired_items(self):
        """ Removes the expired items from the database """
        now = date_to_str(utcnow())
        items = self.get_expired_items(now)

        for item in items:
            logger.info('Removing article {{id: {}, version: {}, type: {}, headline: {}, expired_on: {} }}'.
                        format(item[config.ID_FIELD], item[config.VERSION], item[ITEM_TYPE], item.get('headline', ''),
                               item['expiry']))

            superdesk.get_resource_service('published').remove_expired(item)

    def get_expired_items(self, expired_date_time, limit=100):
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


class UpdateOverdueScheduledPublishedContent(superdesk.Command):
    """
    Update the overdue scheduled stories
    """

    def run(self):
        self.update_overdue_scheduled()

    def update_overdue_scheduled(self):
        """
        Updates the overdue scheduled content on published collection.
        """

        logger.info('Updating overdue scheduled content')

        if is_task_running("publish", "update_overdue_scheduled", UPDATE_OVERDUE_SCHEDULED_DEFAULT):
            return

        try:
            now = date_to_str(utcnow())
            items = get_overdue_scheduled_items(now, 'published')

            for item in items:
                logger.info('updating overdue scheduled article with id {} and headline {} -- expired on: {} now: {}'.
                            format(item[config.ID_FIELD], item['headline'], item['publish_schedule'], now))

                superdesk.get_resource_service('published').\
                    update_published_items(item['item_id'], ITEM_STATE, CONTENT_STATE.PUBLISHED)
        finally:
            mark_task_as_not_running("publish", "update_overdue_scheduled")


superdesk.command('publish:remove_expired', RemoveExpiredPublishContent())
superdesk.command('publish:remove_overdue_scheduled', UpdateOverdueScheduledPublishedContent())
