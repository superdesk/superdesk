# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from collections import namedtuple
import json
import logging
from superdesk import get_resource_service
import superdesk
from superdesk.celery_app import update_key
from superdesk.errors import SuperdeskApiError
from superdesk.metadata.item import not_analyzed, ITEM_STATE, PUBLISH_STATES, EMBARGO
from superdesk.metadata.utils import aggregations
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.utc import utcnow

from bson.objectid import ObjectId
from eve.utils import ParsedRequest, config
from flask import current_app as app

from apps.archive.archive import SOURCE as ARCHIVE
from apps.archive.common import handle_existing_data, item_schema, remove_media_files, get_expiry
from apps.packages import TakesPackageService


logger = logging.getLogger(__name__)

PUBLISHED = 'published'
LAST_PUBLISHED_VERSION = 'last_published_version'
QUEUE_STATE = 'queue_state'
queue_states = ['pending', 'in_progress', 'queued']
PUBLISH_STATE = namedtuple('PUBLISH_STATE', ['PENDING', 'IN_PROGRESS', 'QUEUED'])(*queue_states)

published_item_fields = {
    'item_id': {
        'type': 'string',
        'mapping': not_analyzed
    },
    'publish_state': {
        'type': 'string'
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
    QUEUE_STATE: {
        'type': 'string',
        'default': 'pending',
        'allowed': queue_states,
    },
    'is_take_item': {
        'type': 'boolean',
        'default': False,
    },
    'digital_item_id': {
        'type': 'string'
    },
    'publish_sequence_no': {
        'type': 'integer',
        'readonly': True
    },
    'last_queue_event': {
        'type': 'datetime'
    }
}


class PublishedItemResource(Resource):
    datasource = {
        'search_backend': 'elastic',
        'aggregations': aggregations,
        'default_sort': [('_updated', -1)],
        'projection': {
            'old_version': 0,
            'last_version': 0
        }
    }

    schema = item_schema(published_item_fields)
    etag_ignore_fields = [config.ID_FIELD, 'highlights', 'item_id', LAST_PUBLISHED_VERSION]

    privileges = {'POST': 'publish_queue', 'PATCH': 'publish_queue'}
    item_methods = ['GET', 'PATCH']
    additional_lookup = {
        'url': 'regex("[\w,.:-]+")',
        'field': 'item_id'
    }


class PublishedItemService(BaseService):
    """
    PublishedItemService class is the base class for ArchivedService.
    """
    SEQ_KEY_NAME = 'published_item_sequence_no'

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
            self.raise_if_not_marked_for_publication(doc)
            doc[config.LAST_UPDATED] = doc[config.DATE_CREATED] = utcnow()
            self.set_defaults(doc)

    def on_update(self, updates, original):
        if ITEM_STATE in updates:
            self.raise_if_not_marked_for_publication(updates)

    def raise_if_not_marked_for_publication(self, doc):
        """
        Item should be one of the PUBLISH_STATES. If not raise error.
        """
        if doc.get(ITEM_STATE) not in PUBLISH_STATES:
            raise SuperdeskApiError.badRequestError('Invalid state ({}) for the Published item.'
                                                    .format(doc.get(ITEM_STATE)))

    def set_defaults(self, doc):
        doc['item_id'] = doc[config.ID_FIELD]
        doc['versioncreated'] = utcnow()
        doc['publish_sequence_no'] = update_key(self.SEQ_KEY_NAME, flag=True)

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

    def delete_by_article_id(self, _id):
        """
        Removes the article from the published collection.
        Removes published queue entries and media files.
        :param str _id: id of the document to be deleted. In mongo, it is the item_id
        """
        lookup = {'item_id': _id}
        docs = list(self.get_from_mongo(req=None, lookup=lookup))
        self.delete(lookup=lookup)
        get_resource_service('publish_queue').delete_by_article_id(_id)
        for doc in docs:
            remove_media_files(doc)

    def find_one(self, req, **lookup):
        item = super().find_one(req, **lookup)
        handle_existing_data(item)

        return item

    def __set_published_item_expiry(self, doc):
        """
        Set the expiry for the published item
        :param dict doc: doc on which publishing action is performed
        """
        desk_id = doc.get('task', {}).get('desk', None)
        stage_id = doc.get('task', {}).get('stage', None)

        doc['expiry'] = get_expiry(desk_id, stage_id, offset=doc.get(EMBARGO, doc.get('publish_schedule')))

    def move_to_archived(self, _id):
        published_items = list(self.get_from_mongo(req=None, lookup={'item_id': _id}))
        if not published_items:
            return
        get_resource_service('archived').post(published_items)
        self.delete_by_article_id(_id)
