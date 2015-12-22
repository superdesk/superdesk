# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging

from bson.objectid import ObjectId

import superdesk
from copy import deepcopy
from flask import current_app as app
from eve.utils import ParsedRequest
from eve.versioning import versioned_id_field
from superdesk.celery_app import celery
from superdesk import get_resource_service, config
from superdesk.celery_task_utils import get_lock_id
from .resource import LEGAL_ARCHIVE_NAME, LEGAL_ARCHIVE_VERSIONS_NAME, LEGAL_PUBLISH_QUEUE_NAME
from superdesk.users.services import get_display_name
from apps.archive.common import ARCHIVE
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE
from superdesk.lock import lock, unlock

logger = logging.getLogger(__name__)


class LegalArchiveImport:

    log_msg_format = "{{'_id': {_id}, 'unique_name': {unique_name}, 'version': {_current_version}, " \
                     "'expired_on': {expiry}}}."

    def upsert_into_legal_archive(self, doc):
        """
        Once publish actions are performed on the article do the below:
            1.  Get legal archive article.
            2.  De-normalize the expired article
            3.  Upserting Legal Archive.
            4.  Get Version History and De-normalize and Inserting Legal Archive Versions
        :param dict doc: doc from 'archive' collection.
        """

        if not doc.get(ITEM_STATE) in {CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED, CONTENT_STATE.KILLED}:
            logger.exception('Invalid state: {}. Cannot move the item to legal archive. item: {}'.
                             format(doc.get(ITEM_STATE), self.log_msg_format.format(**doc)))
            return

        # required for behave test.
        legal_archive_doc = deepcopy(doc)

        legal_archive_service = get_resource_service(LEGAL_ARCHIVE_NAME)
        legal_archive_versions_service = get_resource_service(LEGAL_ARCHIVE_VERSIONS_NAME)

        log_msg = self.log_msg_format.format(**legal_archive_doc)
        version_id_field = versioned_id_field(app.config['DOMAIN'][ARCHIVE])
        logger.info('Preparing Article to be inserted into Legal Archive ' + log_msg)

        # Removing Irrelevant properties
        legal_archive_doc.pop(config.ETAG, None)
        legal_archive_doc.pop('lock_user', None)
        legal_archive_doc.pop('lock_session', None)
        legal_archive_doc.pop('lock_time', None)

        logger.info('Removed irrelevant properties from the article {}'.format(log_msg))

        # Step 1
        article_in_legal_archive = legal_archive_service.find_one(req=None, _id=legal_archive_doc[config.ID_FIELD])

        # Step 2 - De-normalizing the legal archive doc
        self._denormalize_user_desk(legal_archive_doc, log_msg)
        logger.info('De-normalized article {}'.format(log_msg))

        # Step 3 - Upserting Legal Archive
        logger.info('Upserting Legal Archive Repo with article {}'.format(log_msg))

        if article_in_legal_archive:
            legal_archive_service.put(legal_archive_doc[config.ID_FIELD], legal_archive_doc)
        else:
            legal_archive_service.post([legal_archive_doc])

        # Step 4 - Get Version History and De-normalize and Inserting Legal Archive Versions
        lookup = {version_id_field: legal_archive_doc[config.ID_FIELD]}
        version_history = list(get_resource_service('archive_versions').get(req=None, lookup=lookup))
        legal_version_history = list(legal_archive_versions_service.get(req=None, lookup=lookup))

        logger.info('Fetched version history for article {}'.format(log_msg))
        versions_to_insert = [version for version in version_history
                              if not any(legal_version for legal_version in legal_version_history
                                         if version[config.VERSION] == legal_version[config.VERSION])]

        # This happens when user kills an article from Dusty Archive
        if article_in_legal_archive and article_in_legal_archive[config.VERSION] < legal_archive_doc[config.VERSION] \
                and len(versions_to_insert) == 0:
            resource_def = app.config['DOMAIN'][ARCHIVE]
            versioned_doc = deepcopy(legal_archive_doc)
            versioned_doc[versioned_id_field(resource_def)] = legal_archive_doc[config.ID_FIELD]
            versioned_doc[config.ID_FIELD] = ObjectId()
            versions_to_insert.append(versioned_doc)

        for version_doc in versions_to_insert:
            self._denormalize_user_desk(version_doc,
                                        self.log_msg_format.format(_id=version_doc[version_id_field],
                                                                   unique_name=version_doc.get('unique_name'),
                                                                   _current_version=version_doc[config.VERSION],
                                                                   expiry=version_doc.get('expiry')))
            version_doc.pop(config.ETAG, None)

        if versions_to_insert:
            legal_archive_versions_service.post(versions_to_insert)
            logger.info('Inserted de-normalized version history for article {}'.format(log_msg))

        logger.info('Upsert completed for article ' + log_msg)

    def _denormalize_user_desk(self, legal_archive_doc, log_msg):
        """
        De-normalizes user, desk and stage details in legal_archive_doc.
        """

        # De-normalizing User Details
        legal_archive_doc['original_creator'] = self.__get_user_name(legal_archive_doc.get('original_creator'))
        legal_archive_doc['version_creator'] = self.__get_user_name(legal_archive_doc.get('version_creator'))

        logger.info('De-normalized User Details for article {}'.format(log_msg))

        # De-normalizing Desk and Stage details
        if legal_archive_doc.get('task'):
            if legal_archive_doc['task'].get('desk'):
                desk = get_resource_service('desks').find_one(req=None, _id=str(legal_archive_doc['task']['desk']))
                if desk:
                    legal_archive_doc['task']['desk'] = desk.get('name')
                    logger.info('De-normalized Desk Details for article {}'.format(log_msg))
                else:
                    logger.info('Desk Details Not Found: {}. {}'.format(legal_archive_doc['task'].get('desk'), log_msg))

            if legal_archive_doc['task'].get('stage'):
                stage = get_resource_service('stages').find_one(req=None, _id=str(legal_archive_doc['task']['stage']))
                if stage:
                    legal_archive_doc['task']['stage'] = stage.get('name')
                    logger.info('De-normalized Stage Details for article {}'.format(log_msg))
                else:
                    logger.info('Stage Details Not Found: {}. {}'.format(legal_archive_doc['task'].get('stage'),
                                                                         log_msg))

            legal_archive_doc['task']['user'] = self.__get_user_name(legal_archive_doc['task'].get('user'))

    def __get_user_name(self, user_id):
        """
        Retrieves display_name of the user identified by user_id
        """
        logger.info('Get User Details for ID:{}'.format(user_id))

        if not user_id:
            return ''

        user = get_resource_service('users').find_one(req=None, _id=user_id)

        if not user:
            return ''

        return get_display_name(user)

    def import_legal_publish_queue(self):
        """
        Import legal publish queue.
        """
        logger.info('Starting to import publish queue items...')
        max_date = self._get_max_date_from_publish_queue()
        logger.info('Get publish queue items from datetime - {}'.format(max_date))
        queue_items = list(self._get_publish_queue_items_to_import(max_date))

        if len(queue_items) == 0:
            logger.info('No Items to import.')
            return

        logger.info('Items to import {}.'.format(len(queue_items)))
        logger.info('Get subscribers info for de-normalising queue items.')
        subscriber_ids = list({str(queue_item['subscriber_id']) for queue_item in queue_items})
        query = {'$and': [{config.ID_FIELD: {'$in': subscriber_ids}}]}
        subscribers = list(get_resource_service('subscribers').get(req=None, lookup=query))
        subscribers = {str(subscriber[config.ID_FIELD]): subscriber for subscriber in subscribers}

        for queue_item in queue_items:
            try:
                self._upsert_into_legal_archive_publish_queue(queue_item, subscribers)
            except:
                logger.exception("Failed to import publish queue item. {}".format(queue_item.get(config.ID_FIELD)))

        logger.info('Completed importing of publish queue items {}.'.format(max_date))

    def _get_publish_queue_items_to_import(self, max_date):
        """
        Get the queue items to import after max_date
        :param datetime max_date:
        :return : list of publish queue items
        """
        legal_publish_queue_service = get_resource_service('publish_queue')

        lookup = {}
        if max_date:
            lookup[config.LAST_UPDATED] = {'$gte': max_date}

        return legal_publish_queue_service.get(req=None, lookup=lookup)

    def _get_max_date_from_publish_queue(self):
        """
        Get the max _updated date from legal_publish_queue collection
        :return datetime: _updated time
        """
        legal_publish_queue_service = get_resource_service(LEGAL_PUBLISH_QUEUE_NAME)
        req = ParsedRequest()
        req.sort = '[("%s", -1)]' % config.LAST_UPDATED
        req.max_results = 1
        req.page = 1
        queue_item = list(legal_publish_queue_service.get(req=req, lookup={}))
        return queue_item[0][config.LAST_UPDATED] if queue_item else None

    def _upsert_into_legal_archive_publish_queue(self, queue_item, subscribers):
        """
        Upsert into legal publish queue.
        :param dict queue_item: publish_queue collection item
        :param dict subscribers: subscribers information
        """
        legal_publish_queue_service = get_resource_service(LEGAL_PUBLISH_QUEUE_NAME)
        legal_queue_item = queue_item.copy()
        lookup = {
            'item_id': legal_queue_item['item_id'],
            'item_version': legal_queue_item['item_version'],
            'subscriber_id': legal_queue_item['subscriber_id']
        }

        log_msg = '{item_id} -- version {item_version} -- subscriber {subscriber_id}.'.format(**lookup)

        logger.info('Processing queue item: {}'.format(log_msg))

        existing_queue_item = legal_publish_queue_service.find_one(req=None, _id=legal_queue_item.get(config.ID_FIELD))
        legal_queue_item['subscriber_id'] = subscribers[str(queue_item['subscriber_id'])]['name']
        legal_queue_item['_subscriber_id'] = queue_item['subscriber_id']

        legal_queue_item.pop(config.ETAG, None)

        if not existing_queue_item:
            legal_publish_queue_service.post([legal_queue_item])
            logger.info('Inserted queue item: {}'.format(log_msg))
        else:
            legal_publish_queue_service.put(existing_queue_item.get(config.ID_FIELD), legal_queue_item)
            logger.info('Updated queue item: {}'.format(log_msg))

        logger.info('Processed queue item: {}'.format(log_msg))


@celery.task(bind=True)
def import_into_legal_archive(self, doc):
    """
    Called async to import into legal archive.
    :param self: celery task
    :param dict doc: document to import into legal_archive
    """
    try:
        LegalArchiveImport().upsert_into_legal_archive(doc)
    except:
        logger.exception("Failed to import into legal archive.")


class ImportLegalPublishQueueCommand(superdesk.Command):
    """
    This command import publish queue records into legal publish queue.
    """
    def run(self):
        logger.info('Importing Legal Publish Queue')
        lock_name = get_lock_id('legal_archive', 'import_legal_publish_queue')
        if not lock(lock_name, '', expire=600):
            return
        try:
            LegalArchiveImport().import_legal_publish_queue()
        finally:
            unlock(lock_name, '')


superdesk.command('legal_publish_queue:import', ImportLegalPublishQueueCommand())
