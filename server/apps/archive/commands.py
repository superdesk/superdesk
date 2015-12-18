# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from superdesk.notification import push_notification

import superdesk
import logging
from eve.utils import ParsedRequest, date_to_str, config

from apps.packages import PackageService
from superdesk.celery_task_utils import is_task_running, mark_task_as_not_running, get_lock_id
from superdesk.utc import utcnow
from .archive import SOURCE as ARCHIVE
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE, ITEM_TYPE, CONTENT_TYPE
from superdesk.metadata.packages import PACKAGE_TYPE, TAKES_PACKAGE
from superdesk.lock import lock, unlock
from superdesk import get_resource_service

logger = logging.getLogger(__name__)

UPDATE_OVERDUE_SCHEDULED_DEFAULT = {'minutes': 10}


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


class RemoveExpiredContent(superdesk.Command):

    def run(self):
        now = utcnow()
        expiry_time_log_msg = 'Expiry Time: {}.'.format(now)
        logger.info('{} Starting to remove expired content at.'.format(expiry_time_log_msg))
        lock_name = get_lock_id('archive', 'remove_expired')
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
        Remove the expired items.
        :param datetime expiry_datetime: expiry datetime
        :param str log_msg: log message to be prefixed
        """
        logger.info('{} Starting to remove published expired items.'.format(log_msg))
        archive_service = get_resource_service(ARCHIVE)
        published_service = get_resource_service('published')

        expired_items = list(archive_service.get_expired_items(expiry_datetime))
        if len(expired_items) == 0:
            logger.info('{} No items found to expire.'.format(log_msg))
            return

        # Step 1: Get the killed Items
        spiked_killed_items = [item for item in expired_items
                               if item.get(ITEM_STATE) in {CONTENT_STATE.KILLED, CONTENT_STATE.SPIKED}]

        items_to_remove = set()
        items_to_be_archived = set()

        # Step 2: Get the not killed and spiked items
        not_killed_items = [item for item in expired_items
                            if item.get(ITEM_STATE) not in {CONTENT_STATE.KILLED, CONTENT_STATE.SPIKED}]

        log_msg_format = "{{'_id': {_id}, 'unique_name': {unique_name}, 'version': {_current_version}, " \
                         "'expired_on': {expiry}}}."

        # Step 3: Processing items to expire
        for item in not_killed_items:
            item_id = item.get(config.ID_FIELD)
            expiry_msg = log_msg_format.format(**item)
            logger.info('{} Processing expired item. {}'.format(log_msg, expiry_msg))

            processed_items = set()
            if item_id not in items_to_be_archived and self._can_remove_item(item, processed_items):
                # item can be archived and removed from the database
                logger.info('{} Removing item. {}'.format(log_msg, expiry_msg))
                logger.info('{} Items to be removed. {}'.format(log_msg, processed_items))
                items_to_be_archived = items_to_be_archived | processed_items

        # move to archived collection
        logger.info('{} Archiving items.'.format(log_msg))
        for item in items_to_be_archived:
            self._move_to_archived(item, log_msg)

        for item in spiked_killed_items:
            # delete from the published collection and queue
            msg = log_msg_format.format(**item)
            try:
                if item.get(ITEM_STATE) == CONTENT_STATE.KILLED:
                    published_service.delete_by_article_id(item.get(config.ID_FIELD))
                    logger.info('{} Deleting killed item from published. {}'.format(log_msg, msg))

                items_to_remove.add(item.get(config.ID_FIELD))
            except:
                logger.exception('{} Failed to delete killed item from published. {}'.format(log_msg, msg))

        archive_service.delete_by_article_ids(list(items_to_remove))
        logger.info('{} Deleting killed and spiked items from archive.'.format(log_msg))

    def _can_remove_item(self, item, processed_item=None):
        """
        Recursively checks if the item can be removed.
        :param dict item: item to be remove
        :param set processed_item: processed items
        :return: True if item can be removed, False otherwise.
        """

        if processed_item is None:
            processed_item = set()

        item_refs = []
        package_service = PackageService()
        archive_service = get_resource_service(ARCHIVE)

        if item.get(ITEM_TYPE) == CONTENT_TYPE.COMPOSITE:
            # Get the item references for is package
            item_refs = package_service.get_residrefs(item)

        if item.get(PACKAGE_TYPE) == TAKES_PACKAGE or \
           item.get(ITEM_TYPE) in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]:
            broadcast_items = get_resource_service('archive_broadcast').get_broadcast_items_from_master_story(item)
            # If master story expires then check if broadcast item is included in a package.
            # If included in a package then check the package expiry.
            item_refs.extend([broadcast_item.get(config.ID_FIELD) for broadcast_item in broadcast_items])

        # get item reference where this referred
        item_refs.extend(package_service.get_linked_in_package_ids(item))

        # check item refs in the ids to remove set
        is_expired = item.get('expiry') < utcnow()

        if is_expired:
            # now check recursively for all references
            if item.get(config.ID_FIELD) in processed_item:
                return is_expired

            processed_item.add(item.get(config.ID_FIELD))
            if item_refs:
                archive_items = archive_service.get_from_mongo(req=None, lookup={'_id': {'$in': item_refs}})
                for archive_item in archive_items:
                    is_expired = self._can_remove_item(archive_item, processed_item)
                    if not is_expired:
                        break

        return is_expired

    def _move_to_archived(self, _id, log_msg):
        """
        Moves all the published version of an article to archived.
        Deletes all published version of an article in the published collection
        :param str _id: id of the document to be moved
        :param str log_msg: log message to be prefixed
        """
        published_service = get_resource_service('published')
        archived_service = get_resource_service('archived')
        archive_service = get_resource_service('archive')

        published_items = list(published_service.get_from_mongo(req=None, lookup={'item_id': _id}))

        try:
            if published_items:
                archived_service.post(published_items)
                logger.info('{} Archived published item'.format(log_msg))
                published_service.delete_by_article_id(_id)
                logger.info('{} Deleted published item.'.format(log_msg))

            archive_service.delete_by_article_ids([_id])
            logger.info('{} Delete archive item.'.format(log_msg))
        except:
            failed_items = [item.get(config.ID_FIELD) for item in published_items]
            logger.exception('{} Failed to move to archived. {}'.format(log_msg, failed_items))


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

superdesk.command('archive:remove_overdue_scheduled', UpdateOverdueScheduledContent())
superdesk.command('archive:remove_expired', RemoveExpiredContent())
