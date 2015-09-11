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
import json

from eve.versioning import versioned_id_field
from eve.utils import ParsedRequest, config
from bson.objectid import ObjectId
from flask import current_app as app

from apps.legal_archive import LEGAL_ARCHIVE_NAME, LEGAL_ARCHIVE_VERSIONS_NAME, LEGAL_PUBLISH_QUEUE_NAME
from apps.packages.package_service import PackageService
import superdesk
from apps.packages import TakesPackageService
from superdesk.users.services import get_display_name
from superdesk.notification import push_notification
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.metadata.item import not_analyzed, ITEM_STATE, CONTENT_STATE, ITEM_TYPE, CONTENT_TYPE, EMBARGO
from apps.archive.common import handle_existing_data, item_schema
from superdesk.metadata.utils import aggregations
from apps.archive.archive import SOURCE as ARCHIVE
from superdesk.utc import utcnow, get_expiry_date
from superdesk import get_resource_service

logger = logging.getLogger(__name__)
LAST_PUBLISHED_VERSION = 'last_published_version'


class PublishedItemResource(Resource):
    datasource = {
        'search_backend': 'elastic',
        'aggregations': aggregations,
        'elastic_filter': {'and': [{'term': {'allow_post_publish_actions': True}},
                                   {'terms': {ITEM_STATE: [CONTENT_STATE.SCHEDULED, CONTENT_STATE.PUBLISHED,
                                                           CONTENT_STATE.KILLED, CONTENT_STATE.CORRECTED]}}]},
        'default_sort': [('_updated', -1)],
        'projection': {
            'old_version': 0,
            'last_version': 0
        }
    }

    published_item_fields = {
        'item_id': {
            'type': 'string',
            'mapping': not_analyzed
        },

        # last_published_version field is set to true for last published version of the item in the published collection
        # and for the older version is set to false. This field is used to display the last version of the digital copy
        # in the published view.
        LAST_PUBLISHED_VERSION: {
            'type': 'boolean',
            'default': True
        },
        'rewritten_by': {
            'type': 'string',
            'mapping': not_analyzed,
            'nullable': True
        },

        # This field is set to False if the item is expired and is not killed after publishing/correcting.
        'allow_post_publish_actions': {
            'type': 'boolean',
            'default': True
        },

        # This field is set to True, when user uses "delete from archived" option.
        # When the article is expired, 'can be removed' flag is True and 'allow post publish actions' flag is False
        # then the article will be removed from published collection.
        'can_be_removed': {
            'type': 'boolean',
            'default': False
        }
    }

    schema = item_schema(published_item_fields)
    etag_ignore_fields = [config.ID_FIELD, 'highlights', 'item_id', LAST_PUBLISHED_VERSION]

    privileges = {'POST': 'publish_queue', 'PATCH': 'publish_queue'}

    additional_lookup = {
        'url': 'regex("[\w,.:-]+")',
        'field': 'item_id'
    }


class PublishedItemService(BaseService):
    def on_fetched(self, docs):
        """
        Overriding this to enhance the published article with the one in archive collection
        """

        self.enhance_with_archive_items(docs[config.ITEMS])

    def on_fetched_item(self, doc):
        """
        Overriding this to enhance the published article with the one in archive collection
        """

        self.enhance_with_archive_items([doc])

    def on_create(self, docs):
        """
        An article can be published multiple times in its lifetime. So, it's necessary to preserve the _id which comes
        from archive collection. Also, sets the expiry on the published item and removes the lock information.
        """

        for doc in docs:
            doc['_created'] = utcnow()
            self.set_defaults(doc)

    def set_defaults(self, doc):
        doc['item_id'] = doc[config.ID_FIELD]
        doc['versioncreated'] = utcnow()

        self.__set_published_item_expiry(doc)

        doc.pop(config.ID_FIELD, None)
        doc.pop('lock_user', None)
        doc.pop('lock_time', None)
        doc.pop('lock_session', None)

    def enhance_with_archive_items(self, items):
        if items:
            ids = list(set([item.get('item_id') for item in items if item.get('item_id')]))
            archive_items = []
            if ids:
                query = {'$and': [{config.ID_FIELD: {'$in': ids}}]}
                archive_req = ParsedRequest()
                archive_req.max_results = len(ids)
                # can't access published from elastic due filter on the archive resource hence going to mongo
                archive_items = list(superdesk.get_resource_service(ARCHIVE)
                                     .get_from_mongo(req=archive_req, lookup=query))

                takes_service = TakesPackageService()
                for item in archive_items:
                    handle_existing_data(item)
                    takes_service.enhance_with_package_info(item)

            for item in items:
                archive_item = [i for i in archive_items if i.get(config.ID_FIELD) == item.get('item_id')]
                archive_item = archive_item[0] if len(archive_item) > 0 else \
                    {config.VERSION: item.get(config.VERSION, 1)}

                updates = {
                    config.ID_FIELD: item.get('item_id'),
                    'item_id': item.get(config.ID_FIELD),
                    'lock_user': archive_item.get('lock_user', None),
                    'lock_time': archive_item.get('lock_time', None),
                    'lock_session': archive_item.get('lock_session', None),
                    'archive_item': archive_item if archive_item else None
                }

                item.update(updates)
                handle_existing_data(item)

    def on_delete(self, doc):
        """
        Deleting a published item has a workflow which is implemented in remove_expired().
        Overriding to avoid other services from invoking this method accidentally.
        """

        if app.testing:
            super().on_delete(doc)
        else:
            raise NotImplementedError("Deleting a published item has a workflow which is "
                                      "implemented in remove_expired().")

    def delete_action(self, lookup=None):
        """
        Deleting a published item has a workflow which is implemented in remove_expired().
        Overriding to avoid other services from invoking this method accidentally.
        """

        if app.testing:
            super().delete_action(lookup)
        else:
            raise NotImplementedError("Deleting a published item has a workflow which is "
                                      "implemented in remove_expired().")

    def on_deleted(self, doc):
        """
        Deleting a published item has a workflow which is implemented in remove_expired().
        Overriding to avoid other services from invoking this method accidentally.
        """

        if app.testing:
            super().on_deleted(doc)
        else:
            raise NotImplementedError("Deleting a published item has a workflow which is "
                                      "implemented in remove_expired().")

    def get_other_published_items(self, _id):
        try:
            query = {'query': {'filtered': {'filter': {'term': {'item_id': _id}}}}}
            request = ParsedRequest()
            request.args = {'source': json.dumps(query)}
            return super().get(req=request, lookup=None)
        except:
            return []

    def get_rewritten_take_packages_per_event(self, event_id):
        """ Returns all the published and rewritten take stories for the same event """
        try:
            query = {'query':
                     {'filtered':
                      {'filter':
                       {'bool':
                        {'must': [
                            {'term': {'package_type': 'takes'}},
                            {'term': {'event_id': event_id}},
                            {'exists': {'field': 'rewritten_by'}}
                        ]}}}}}

            request = ParsedRequest()
            request.args = {'source': json.dumps(query)}
            return super().get(req=request, lookup=None)
        except:
            return []

    def get_rewritten_items_by_event_story(self, event_id, rewrite_id):
        """ Returns all the published and rewritten stories for the given event and rewrite_id"""
        try:
            query = {'query':
                     {'filtered':
                      {'filter':
                       {'bool':
                        {'must': [
                            {'term': {'event_id': event_id}},
                            {'term': {'rewritten_by': rewrite_id}}
                        ]}}}}}

            request = ParsedRequest()
            request.args = {'source': json.dumps(query)}
            return super().get(req=request, lookup=None)
        except:
            return []

    def is_rewritten_before(self, item_id):
        """ Checks if the published item is rewritten before
        :param _id: item_id of the published item
        :return: True is it is rewritten before
        """
        doc = self.find_one(req=None, item_id=item_id)
        return doc and 'rewritten_by' in doc and doc['rewritten_by']

    def update_published_items(self, _id, field, state):
        items = self.get_other_published_items(_id)
        for item in items:
            try:
                super().system_update(ObjectId(item[config.ID_FIELD]), {field: state}, item)
            except:
                # This part is used in unit testing
                super().system_update(item[config.ID_FIELD], {field: state}, item)

    def delete_by_article_id(self, _id, doc=None):
        if doc is None:
            doc = self.find_one(req=None, item_id=_id)

        self.delete(lookup={config.ID_FIELD: doc[config.ID_FIELD]})

    def find_one(self, req, **lookup):
        item = super().find_one(req, **lookup)
        handle_existing_data(item)

        return item

    def __set_published_item_expiry(self, doc):
        desk_id = doc.get('task', {}).get('desk', None)
        desk = {}

        if desk_id:
            desk = get_resource_service('desks').find_one(req=None, _id=desk_id)

        expiry_minutes = desk.get('published_item_expiry', config.PUBLISHED_ITEMS_EXPIRY_MINUTES)
        doc['expiry'] = get_expiry_date(expiry_minutes, offset=doc[EMBARGO]) if doc.get(EMBARGO) else \
            get_expiry_date(expiry_minutes)

    def remove_expired(self, doc):
        """
        Removes the expired published article from 'published' collection. Below is the workflow:
            1.  Update allow_post_publish_actions, can_be_removed flags.
            2.  Inserts/updates the article in Legal Archive repository
                (a) All references to master data like users, desks ... is de-normalized and then
                    inserted into Legal Archive. Same is done to each version of the article.
                (b) Inserts Formatted Items
                (c) Inserts Transmission Details (fetched from publish_queue collection)
            3.  Removes the item from publish_queue and published collections, if can_be_removed is True
            4.  Remove the article and its versions from archive collection if all of the below conditions are met:
                (a) Article hasn't been published/corrected/killed again
                (b) Article isn't part of a package

        :param doc: doc in 'published' collection
        """

        logging.info("Starting the workflow for removing the expired publish item with id: %s" % doc['item_id'])

        can_be_removed = doc['can_be_removed']

        if not can_be_removed:
            # Step 1
            updates = self._update_flags(doc)
            doc.update(updates)
            can_be_removed = updates.get('can_be_removed', can_be_removed)

            # Step 2
            publish_queue_items = self._upsert_into_legal_archive(doc)
            for publish_queue_item in publish_queue_items:
                get_resource_service('publish_queue').delete_action(
                    lookup={config.ID_FIELD: publish_queue_item[config.ID_FIELD]})

            # Step 4
            if self.can_remove_from_production(doc):
                resource_def = app.config['DOMAIN']['archive_versions']
                lookup = {'$and': [{versioned_id_field(resource_def): doc['item_id']},
                                   {config.VERSION: {'$lte': doc[config.VERSION]}}]}
                get_resource_service('archive_versions').delete(lookup)

                get_resource_service(ARCHIVE).delete_action({config.ID_FIELD: doc['item_id']})

        if can_be_removed:
            # Step 3
            self.delete_by_article_id(_id=doc['item_id'], doc=doc)

        logging.info("Completed the workflow for removing the expired publish item with id: %s" % doc['item_id'])

    def _update_flags(self, doc):
        """
        Update allow_post_publish_actions to False. Also, update can_be_removed to True if item is killed.

        :param doc: expired item from published collection.
        :return: updated flag values as dict
        """

        flag_updates = {'allow_post_publish_actions': False, '_updated': utcnow()}
        super().patch(doc[config.ID_FIELD], flag_updates)
        push_notification('item:published:no_post_publish_actions', item=str(doc[config.ID_FIELD]))

        update_can_be_removed = (doc[ITEM_STATE] == CONTENT_STATE.KILLED)
        if doc.get(ITEM_STATE) in [CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED]:
            # query to check if the item is killed the future versions or not
            query = {
                'query': {
                    'filtered': {
                        'filter': {
                            'and': [
                                {'term': {'item_id': doc['item_id']}},
                                {'term': {ITEM_STATE: CONTENT_STATE.KILLED}}
                            ]
                        }
                    }
                }
            }

            request = ParsedRequest()
            request.args = {'source': json.dumps(query)}
            items = super().get(req=request, lookup=None)

            update_can_be_removed = (items.count() > 0)

        if update_can_be_removed:
            get_resource_service('archived').delete_action({config.ID_FIELD: doc[config.ID_FIELD]})
            flag_updates['can_be_removed'] = True

        logger.info('Updated flags for the published item {} with headline {} and version {} and expiry {}.'.format(
            doc['item_id'], doc.get('headline'), doc[config.VERSION], doc['expiry']))

        return flag_updates

    def _upsert_into_legal_archive(self, doc):
        """
        For the expired published article represented by doc, do the below:
            1.  Fetch version history of article so that version_history_doc[config.VERSION] <= doc[config.VERSION].
            2.  De-normalize the expired article and each version of the article
            3.  Fetch Transmission Details so that queued_item['item_version'] == doc[config.VERSION]
            4.  De-normalize the Transmission Details
            5.  An article can be published more than time before it's removed from production database, it's important
                to check if the article already exists in Legal Archive DB. If exists then replace the article in
                Legal Archive DB, otherwise create.
            6.  Create the Version History of the article in Legal Archive DB.
            7.  Create the Transmission Details in Legal Archive DB.

        :param: doc - expired doc from 'published' collection.
        :return: transmission details
        """

        legal_archive_doc = doc.copy()
        logging.info('Preparing Article to be inserted into Legal Archive %s' % legal_archive_doc.get('unique_name'))

        # Removing Irrelevant properties
        legal_archive_doc[config.ID_FIELD] = legal_archive_doc['item_id']
        del legal_archive_doc[config.ETAG]
        del legal_archive_doc['item_id']

        logging.info('Removed Irrelevant properties from the article %s' % legal_archive_doc.get('unique_name'))

        # Step 3 - Fetch Publish Queue Items
        lookup = {'item_id': legal_archive_doc[config.ID_FIELD], 'item_version': legal_archive_doc[config.VERSION]}
        queue_items = list(get_resource_service('publish_queue').get(req=None, lookup=lookup))
        assert len(queue_items) > 0, \
            "Transmission Details are empty for published item %s" % legal_archive_doc[config.ID_FIELD]
        logging.info('Fetched transmission details for article %s' % legal_archive_doc.get('unique_name'))

        # Step 4
        subscriber_ids = list({str(queue_item['subscriber_id']) for queue_item in queue_items})
        query = {'$and': [{config.ID_FIELD: {'$in': subscriber_ids}}]}
        subscribers = list(get_resource_service('subscribers').get(req=None, lookup=query))
        subscribers = {str(subscriber[config.ID_FIELD]): subscriber for subscriber in subscribers}

        for queue_item in queue_items:
            del queue_item[config.ETAG]
            queue_item['subscriber_id'] = subscribers[str(queue_item['subscriber_id'])]['name']
        logging.info(
            'De-normalized the Transmission Detail records of article %s' % legal_archive_doc.get('unique_name'))

        # Step 2 - De-normalizing the legal archive doc
        self._denormalize_user_desk(legal_archive_doc)

        # Step 1 - Get Version History
        req = ParsedRequest()
        req.sort = '[("%s", 1)]' % config.VERSION
        resource_def = app.config['DOMAIN']['archive_versions']
        lookup = {'$and': [{versioned_id_field(resource_def): legal_archive_doc[config.ID_FIELD]},
                           {config.VERSION: {'$lte': legal_archive_doc[config.VERSION]}}]}

        version_history = get_resource_service('archive_versions').get(req=req, lookup=lookup)
        legal_archive_doc_versions = []
        for versioned_doc in version_history:
            self._denormalize_user_desk(versioned_doc)
            del versioned_doc[config.ETAG]
            legal_archive_doc_versions.append(versioned_doc)
        logging.info('Fetched version history for article %s' % legal_archive_doc.get('unique_name'))

        legal_archive_service = get_resource_service(LEGAL_ARCHIVE_NAME)
        legal_archive_versions_service = get_resource_service(LEGAL_ARCHIVE_VERSIONS_NAME)
        legal_publish_queue_service = get_resource_service(LEGAL_PUBLISH_QUEUE_NAME)

        # Step 5 - Upserting Legal Archive
        logging.info('Upserting Legal Archive Repo with article %s' % legal_archive_doc.get('unique_name'))

        article_in_legal_archive = legal_archive_service.find_one(_id=legal_archive_doc[config.ID_FIELD],
                                                                  req=ParsedRequest())
        if article_in_legal_archive:
            legal_archive_service.put(legal_archive_doc[config.ID_FIELD], legal_archive_doc)
        else:
            legal_archive_service.post([legal_archive_doc])

        # Step 6
        if legal_archive_doc_versions:
            legal_archive_versions_service.post(legal_archive_doc_versions)

        # Step 7
        legal_publish_queue_service.post(queue_items)

        logging.info('Upsert completed for article %s' % legal_archive_doc.get('unique_name'))

        return queue_items

    def _denormalize_user_desk(self, legal_archive_doc):

        # De-normalizing User Details
        if legal_archive_doc.get('original_creator'):
            legal_archive_doc['original_creator'] = self.__get_user_name(legal_archive_doc['original_creator'])

        if legal_archive_doc.get('version_creator'):
            legal_archive_doc['version_creator'] = self.__get_user_name(legal_archive_doc['version_creator'])
        logging.info('De-normalized User Details for article %s' % legal_archive_doc.get('unique_name'))

        # De-normalizing Desk and Stage details
        if legal_archive_doc.get('task'):
            if legal_archive_doc['task'].get('desk'):
                desk = get_resource_service('desks').find_one(req=None, _id=str(legal_archive_doc['task']['desk']))
                legal_archive_doc['task']['desk'] = desk['name']
                logging.info('De-normalized desk details for article %s' % legal_archive_doc.get('unique_name'))

            if legal_archive_doc['task'].get('stage'):
                stage = get_resource_service('stages').find_one(req=None, _id=str(legal_archive_doc['task']['stage']))
                legal_archive_doc['task']['stage'] = stage['name']
                logging.info('De-normalized stage details for article %s' % legal_archive_doc.get('unique_name'))

            if legal_archive_doc['task'].get('user'):
                legal_archive_doc['task']['user'] = self.__get_user_name(legal_archive_doc['task']['user'])

    def __get_user_name(self, user_id):
        """
        Retrieves display_name of the user identified by user_id
        """

        if not user_id:
            return ''

        user = get_resource_service('users').find_one(req=None, _id=user_id)
        return get_display_name(user)

    def can_remove_from_production(self, doc):
        """
        Returns true if the doc in published collection can be removed from production, otherwise returns false.
        1. Returns false if item is published more than once
        2. Returns false if item is referenced by a package
        3. Returns false if the item is package and all items in the package are not found in archived collection.

        :param doc: article in published collection
        :return: True if item can be removed from production, False otherwise.
        """

        items = self.get_other_published_items(doc['item_id'])
        is_removable = (items.count() == 0)

        if is_removable:
            is_removable = (PackageService().get_packages(doc['item_id']).count() == 0)

            if is_removable and doc[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
                return self._can_remove_package_from_production(doc)

        return is_removable

    def _can_remove_package_from_production(self, package):
        """
        Recursively checks if the package can be removed from production.

        :param package:
        :return: True if item can be removed from production, False otherwise.
        """

        item_refs = PackageService().get_residrefs(package)
        archived_items = list(get_resource_service('archived').find_by_item_ids(item_refs))
        is_removable = (len(item_refs) == len(archived_items))

        if is_removable:
            packages_in_archived_items = (p for p in archived_items if p[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE)

            for package in packages_in_archived_items:
                is_removable = self._can_remove_package_from_production(package)
                if not is_removable:
                    break

        return is_removable
