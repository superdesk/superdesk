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

from eve.utils import date_to_str, config
import superdesk
from superdesk.celery_task_utils import is_task_running, mark_task_as_not_running
from superdesk.utc import utcnow
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE
from apps.archive.commands import get_overdue_scheduled_items

logger = logging.getLogger(__name__)

REMOVE_SPIKE_DEFAULT = {'minutes': 30}
UPDATE_OVERDUE_SCHEDULED_DEFAULT = {'minutes': 10}


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


superdesk.command('publish:remove_overdue_scheduled', UpdateOverdueScheduledPublishedContent())
