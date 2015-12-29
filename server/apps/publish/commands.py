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
from apps.packages.takes_package_service import TakesPackageService
from superdesk import get_resource_service
from superdesk.celery_task_utils import is_task_running, mark_task_as_not_running, get_lock_id
from superdesk.lock import lock, unlock
from superdesk.metadata.packages import RESIDREF
from superdesk.metadata.utils import is_takes_package
from superdesk.notification import push_notification
from superdesk.utc import utcnow
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE
from apps.archive.commands import get_overdue_scheduled_items
from apps.archive.archive import SOURCE as ARCHIVE

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


class RemoveExpiredKilledContent(superdesk.Command):
    """
    When an article is killed from Dusty Archive the normal expiry process doesn't remove the item from published
    collection and this command takes care of such items.
    """

    def run(self):
        now = utcnow()
        expiry_time_log_msg = 'Expiry Time: {}.'.format(now)
        logger.info('{} Starting to remove expired content at.'.format(expiry_time_log_msg))

        lock_name = get_lock_id('published', 'remove_expired')
        if not lock(lock_name, '', expire=600):
            logger.info('{} Remove expired content task is already running.'.format(expiry_time_log_msg))
            return
        try:
            logger.info('{} Removing expired content for expiry.'.format(expiry_time_log_msg))
            self._remove_expired_items(now, expiry_time_log_msg)
        finally:
            unlock(lock_name, '')

        push_notification('content:expired')
        logger.info('{} Completed remove expired content.'.format(expiry_time_log_msg))

    def _remove_expired_items(self, expiry_datetime, log_msg):
        """
        Remove the expired articles from published collection whose state is killed. Below is the workflow:
            1. Fetch articles whose state is killed and expired from published collection
            2. For each expired article:
                a.  Check if the article in production. If available then proceed to next article as Archive Expiry
                    process will take care of it. If not mark the article to be eligible for removal.
                b.  If the expired article is a Takes Package then check if all the takes are expired. If not expired
                    then proceed to next article. If all the takes are expired then mark all the takes and takes package
                    to be eligible for removal.
                c.  If the article has an associated Takes Package then check if the takes package is expired. If not,
                    then proceed to the next article. If expired then repeat Step (b) for the associated Takes Package.
                d.  If the above steps outputs article(s) to be removed then remove them from the published collection.
        :param datetime expiry_datetime: expiry datetime
        :param str log_msg: log message to be prefixed
        """

        logger.info('{} Starting to remove expired items in killed state from published collection.'.format(log_msg))
        published_service = get_resource_service('published')
        archive_service = get_resource_service(ARCHIVE)

        expired_items = list(published_service.get_expired_items(expiry_datetime))
        if len(expired_items) == 0:
            logger.info('{} No items found to expire.'.format(log_msg))
            return

        removed_items = set()
        for item in expired_items:
            item_id = item.get('item_id')
            if item_id not in removed_items:
                removed_items.add(item_id)
                if archive_service.find_one(req=None, _id=item_id):
                    logger.info('Item with id: {} and slugged: {} isn''t killed from archived'
                                .format(item_id, item.get('slugline')))
                else:
                    to_remove = []
                    if is_takes_package(item):
                        if self._are_takes_expired(item, to_remove, removed_items, expiry_datetime):
                            to_remove.append(item_id)
                    else:
                        takes_package_service = TakesPackageService()
                        takes_package_id = takes_package_service.get_take_package_id(item)
                        if takes_package_id:
                            removed_items.add(takes_package_id)
                            takes_package = published_service.find_one(req=None, item_id=takes_package_id)
                            if takes_package.get('expiry') > expiry_datetime:
                                logger.info('Digital Story: {} isn''t expired'.format(takes_package_id))
                            elif self._are_takes_expired(takes_package, to_remove, removed_items, expiry_datetime,
                                                         item_id):
                                to_remove.append(takes_package_id)
                        else:
                            to_remove.append(item_id)

                    for item_id in to_remove:
                        logger.info('Removing killed item with id: {} and slugged: {} from published collection'
                                    .format(item_id, item.get('slugline')))
                        get_resource_service('published').delete({'item_id': item_id})

    def _are_takes_expired(self, takes_package, to_remove, removed_items, expiry_datetime, item_id=None):
        """
        Checks if all the takes in the given takes_package are expired. Each expired article is appended to the given
        to_remove and removed_items collections. Returns True if all of them are expired, otherwise False.

        :param takes_package:
        :type takes_package: dict
        :param to_remove:
        :type to_remove: list
        :param removed_items:
        :type removed_items: set
        :param expiry_datetime: timestamp to be used to check if a take is expired or not
        :type expiry_datetime: datetime
        :param item_id:
        :type item_id:
        :return: True if all of them are expired, otherwise False.
        :rtype: bool
        """

        published_service = get_resource_service('published')
        takes_package_service = TakesPackageService()

        for takes_ref in takes_package_service.get_package_refs(takes_package):
            if takes_ref[RESIDREF] != item_id:
                removed_items.add(takes_ref[RESIDREF])
                take = published_service.find_one(req=None, item_id=takes_ref[RESIDREF])
                if take.get('expiry') < expiry_datetime:
                    to_remove.append(takes_ref[RESIDREF])
                else:
                    logger.info('Take: {} isn''t expired'.format(takes_ref[RESIDREF]))
                    to_remove.clear()
                    return False

        if item_id:
            to_remove.append(item_id)

        return True


superdesk.command('publish:remove_overdue_scheduled', UpdateOverdueScheduledPublishedContent())
superdesk.command('published:remove_killed_if_expired', UpdateOverdueScheduledPublishedContent())
