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
from apps.packages import TakesPackageService
from superdesk.resource import Resource
from superdesk.services import BaseService
from apps.content import not_analyzed
from apps.archive.common import aggregations, handle_existing_data, item_schema
from apps.archive.archive import SOURCE as ARCHIVE
from eve.utils import ParsedRequest, config
from bson.objectid import ObjectId
from superdesk.utc import utcnow, get_expiry_date
import json
import superdesk

logger = logging.getLogger(__name__)


class PublishedItemResource(Resource):
    datasource = {
        'search_backend': 'elastic',
        'aggregations': aggregations,
        'elastic_filter': {'terms': {'state': ['scheduled', 'published', 'killed', 'corrected']}},
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
        'last_publish_action': {'type': 'string'}
    }

    schema = item_schema(published_item_fields)
    etag_ignore_fields = ['_id', 'last_publish_action', 'highlights', 'item_id']
    privileges = {'POST': 'publish_queue', 'PATCH': 'publish_queue'}
    additional_lookup = {
        'url': 'regex("[\w,.:-]+")',
        'field': 'item_id'
    }


class PublishedItemService(BaseService):
    def on_fetched(self, docs):
        """
        Overriding this to handle existing data in Mongo & Elastic.
        There could be a possible performance hit in regards to enhance the documents.
        """
        self.enhance_with_archive_items(docs[config.ITEMS])

    def on_fetched_item(self, doc):
        self.enhance_with_archive_items([doc])

    def on_create(self, docs):
        # the same content can be published more than once
        # so it is necessary to have a new _id and preserve the original
        # storing the _version in last version and delete
        for doc in docs:
            doc['item_id'] = doc['_id']
            doc['_created'] = utcnow()
            doc['versioncreated'] = utcnow()
            self.__set_published_item_expiry(doc)
            doc.pop('_id', None)
            doc.pop('lock_user', None)
            doc.pop('lock_time', None)

    def on_delete(self, doc):
        self.insert_into_text_archive(doc)

    def enhance_with_archive_items(self, items):
        if items:
            ids = list(set([item.get('item_id') for item in items if item.get('item_id')]))
            archive_items = []
            if ids:
                query = {'$and': [{'_id': {'$in': ids}}]}
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
                try:
                    archive_item = [i for i in archive_items if i.get('_id') == item.get('item_id')][0]
                except IndexError:
                    logger.exception(('Data inconsistency found for the published item {}. '
                                      'Cannot find item {} in the archive collection.')
                                     .format(item.get('_id'), item.get('item_id')))
                    archive_item = {}

                updates = {
                    '_id': item.get('item_id'),
                    'item_id': item.get('_id'),
                    'lock_user': archive_item.get('lock_user', None),
                    'lock_time': archive_item.get('lock_time', None),
                    'lock_session': archive_item.get('lock_session', None),
                    'archive_item': archive_item if archive_item else None
                }

                item.update(updates)
                handle_existing_data(item)

    def get_other_published_items(self, _id):
        try:
            query = {'query': {'filtered': {'filter': {'term': {'item_id': _id}}}}}
            request = ParsedRequest()
            request.args = {'source': json.dumps(query)}
            return super().get(req=request, lookup=None)
        except:
            return []

    def is_published_before(self, item_id):
        item = super().find_one(req=None, _id=item_id)
        return 'last_publish_action' in item

    def update_published_items(self, _id, field, state):
        items = self.get_other_published_items(_id)
        for item in items:
            try:
                super().system_update(ObjectId(item['_id']), {field: state}, item)
            except:
                # This part is used in unit testing
                super().system_update(item['_id'], {field: state}, item)

    def delete_by_article_id(self, _id):
        lookup = {'query': {'term': {'item_id': _id}}}
        self.delete(lookup=lookup)

    def insert_into_text_archive(self, doc):
        """
        To move the items into text archive once it is published
        """
        text_archive = superdesk.get_resource_service('text_archive')

        if text_archive is None:
            return

        if doc.get('state') == 'published':
            # query to check if the item is killed the future versions or not
            query = {
                'query': {
                    'filtered': {
                        'filter': {
                            'and': [
                                {'term': {'item_id': doc['item_id']}},
                                {'term': {'state': 'killed'}}
                            ]
                        }
                    }
                }
            }

            request = ParsedRequest()
            request.args = {'source': json.dumps(query)}
            items = super().get(req=request, lookup=None)

            if items.count() == 0:
                text_archive.post([doc.copy()])
                logger.info('Inserting published item {} with headline {} and version {} and expiry {}.'.
                            format(doc['item_id'], doc.get('headline'), doc.get('_version'), doc.get('expiry')))
        elif doc.get('state') == 'killed':
            text_archive.delete_action({'_id': doc['_id']})
            logger.info('Deleting published item {} with headline {} and version {} and expiry {}.'.
                        format(doc['item_id'], doc.get('headline'), doc.get('_version'), doc.get('expiry')))

    def find_one(self, req, **lookup):
        item = super().find_one(req, **lookup)
        handle_existing_data(item)

        return item

    def __set_published_item_expiry(self, doc):
        desk_id = doc.get('task', {}).get('desk', None)
        desk = {}
        if desk_id:
            desk = superdesk.get_resource_service('desks').find_one(req=None, _id=desk_id)
        expiry_minutes = desk.get('published_item_expiry', config.PUBLISHED_ITEMS_EXPIRY_MINUTES)
        doc['expiry'] = get_expiry_date(expiry_minutes)
