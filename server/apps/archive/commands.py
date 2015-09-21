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
from eve.utils import ParsedRequest, date_to_str, config
from superdesk.celery_task_utils import is_task_running, mark_task_as_not_running
from superdesk.utc import utcnow
from .archive import SOURCE as ARCHIVE
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE

logger = logging.getLogger(__name__)

REMOVE_SPIKE_DEFAULT = {'minutes': 30}
UPDATE_OVERDUE_SCHEDULED_DEFAULT = {'minutes': 10}


class RemoveExpiredSpikeContent(superdesk.Command):
    """
    Removes expired articles whose state is 'spiked' form archive.
    """

    def run(self):
        self.remove_expired_content()

    def remove_expired_content(self):
        logger.info('Removing expired content if spiked')

        if is_task_running("archive", "remove_expired_content", REMOVE_SPIKE_DEFAULT):
            return

        try:
            now = date_to_str(utcnow())
            items = self.get_expired_items(now)

            while items.count() > 0:
                for item in items:
                    logger.info('deleting {} expiry: {} now:{}'.format(item[config.ID_FIELD], item['expiry'], now))
                    superdesk.get_resource_service(ARCHIVE).remove_expired(item)

                items = self.get_expired_items(now)

        finally:
            mark_task_as_not_running("archive", "remove_expired_content")

    def get_expired_items(self, now):
        query_filter = self._get_query_for_expired_items(now)
        req = ParsedRequest()
        req.max_results = 100

        return superdesk.get_resource_service(ARCHIVE).get_from_mongo(req=req, lookup=query_filter)

    def _get_query_for_expired_items(self, now):
        query = {
            '$and': [
                {'expiry': {'$lte': now}},
                {ITEM_STATE: CONTENT_STATE.SPIKED}
            ]
        }

        return query


class UpdateOverdueScheduledContent(superdesk.Command):
    """
    Updates the overdue scheduled stories
    """

    def run(self):
        self.update_overdue_scheduled()

    def update_overdue_scheduled(self):
        """
        Updates the overdue scheduled content on archive collection.
        """

        logger.info('Updating overdue scheduled content')

        if is_task_running("archive", "update_overdue_scheduled", UPDATE_OVERDUE_SCHEDULED_DEFAULT):
            return

        try:
            now = date_to_str(utcnow())
            items = get_overdue_scheduled_items(now, ARCHIVE)
            item_update = {ITEM_STATE: CONTENT_STATE.PUBLISHED}

            for item in items:
                logger.info('updating overdue scheduled article with id {} and headline {} -- expired on: {} now: {}'.
                            format(item[config.ID_FIELD], item['headline'], item['publish_schedule'], now))

                superdesk.get_resource_service(ARCHIVE).patch(item['item_id'], item_update)
        finally:
            mark_task_as_not_running("archive", "update_overdue_scheduled")


def get_overdue_scheduled_items(expired_date_time, resource, limit=100):
    """
    Fetches the overdue scheduled articles from given collection. Overdue Conditions:
        1.  it should be in 'scheduled' state
        2.  publish_schedule is less than or equal to expired_date_time

    :param expired_date_time: DateTime that scheduled tate will be checked against
    :param resource: Name of the resource to check the data from
    :param limit: Number of return items
    :return: overdue scheduled articles from published collection
    """

    logger.info('Get overdue scheduled content from {}'.format(resource))
    query = {'$and': [
        {'publish_schedule': {'$lte': expired_date_time}},
        {ITEM_STATE: CONTENT_STATE.SCHEDULED}
    ]}

    req = ParsedRequest()
    req.sort = '_modified'
    req.max_results = limit

    return superdesk.get_resource_service(resource).get_from_mongo(req=req, lookup=query)

superdesk.command('archive:remove_spiked_if_expired', RemoveExpiredSpikeContent())
superdesk.command('archive:remove_overdue_scheduled', UpdateOverdueScheduledContent())
