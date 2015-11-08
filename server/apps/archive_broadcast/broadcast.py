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
import json
from eve.utils import ParsedRequest
from eve.versioning import resolve_document_version
from flask import request
from apps.archive.common import CUSTOM_HATEOAS, insert_into_versions, get_user, \
    ITEM_CREATE, BROADCAST_GENRE, is_genre
from apps.packages import TakesPackageService
from superdesk.resource import Resource, build_custom_hateoas
from superdesk.services import BaseService
from superdesk.metadata.utils import item_url
from superdesk.metadata.item import CONTENT_TYPE, CONTENT_STATE, ITEM_TYPE, ITEM_STATE
from superdesk import get_resource_service, config
from superdesk.errors import SuperdeskApiError
from apps.archive.archive import SOURCE
from apps.publish.content.common import ITEM_CORRECT, ITEM_PUBLISH


logger = logging.getLogger(__name__)
# field to be copied from item to broadcast item
FIELDS_TO_COPY = ['urgency', 'priority', 'anpa_category', 'type',
                  'subject', 'dateline', 'slugline', 'place']
ARCHIVE_BROADCAST_NAME = 'archive_broadcast'


class ArchiveBroadcastResource(Resource):
    endpoint_name = ARCHIVE_BROADCAST_NAME
    resource_title = endpoint_name

    url = 'archive/<{0}:item_id>/broadcast'.format(item_url)
    schema = {
        'desk': Resource.rel('desks', embeddable=False, required=False, nullable=True)
    }
    resource_methods = ['POST']
    item_methods = []
    privileges = {'POST': ARCHIVE_BROADCAST_NAME}


class ArchiveBroadcastService(BaseService):

    takesService = TakesPackageService()

    def create(self, docs):
        service = get_resource_service(SOURCE)
        item_id = request.view_args['item_id']
        item = service.find_one(req=None, _id=item_id)
        doc = docs[0]

        self._valid_broadcast_item(item)

        desk_id = doc.get('desk')
        desk = None

        if desk_id:
            desk = get_resource_service('desks').find_one(req=None, _id=desk_id)

        doc.pop('desk', None)
        doc['task'] = {}
        if desk:
            doc['task']['desk'] = desk.get(config.ID_FIELD)
            doc['task']['stage'] = desk.get('incoming_stage')

        doc['task']['user'] = get_user().get('_id')
        genre_list = get_resource_service('vocabularies').find_one(req=None, _id='genre') or {}
        broadcast_genre = [{'value': genre.get('value'), 'name': genre.get('name')}
                           for genre in genre_list.get('items', [])
                           if genre.get('value') == BROADCAST_GENRE]

        if not broadcast_genre:
            raise SuperdeskApiError.badRequestError(message="Cannot find the {} genre.".format(BROADCAST_GENRE))

        doc['broadcast'] = {
            'status': '',
            'master_id': item_id,
            'takes_package_id': self.takesService.get_take_package_id(item),
            'rewrite_id': item.get('rewritten_by')
        }

        doc['genre'] = broadcast_genre
        doc['family_id'] = item.get('family_id')

        for key in FIELDS_TO_COPY:
            doc[key] = item.get(key)

        resolve_document_version(document=doc, resource=SOURCE, method='POST')
        service.post(docs)
        insert_into_versions(id_=doc[config.ID_FIELD])
        build_custom_hateoas(CUSTOM_HATEOAS, doc)
        return [doc[config.ID_FIELD]]

    def _valid_broadcast_item(self, item):
        """
        Broadcast item can only be created for Text or Pre-formatted item.
        Item state needs to be Published or Corrected
        :param dict item: Item from which the broadcast item will be created
        """
        if not item:
            raise SuperdeskApiError.notFoundError(
                message="Cannot find the requested item id.")

        if not item.get(ITEM_TYPE) in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]:
            raise SuperdeskApiError.badRequestError(message="Invalid content type.")

        if item.get(ITEM_STATE) not in [CONTENT_STATE.CORRECTED, CONTENT_STATE.PUBLISHED]:
            raise SuperdeskApiError.badRequestError(message="Invalid content state.")

    def _get_broadcast_items(self, ids):
        """
        Get the broadcast items for the master_id and takes_package_id
        :param list ids: list of item ids
        :return list: list of broadcast items
        """
        query = {
            'query': {
                'filtered': {
                    'filter': {
                        'bool': {
                            'must': {'term': {'genre.name': BROADCAST_GENRE}},
                            'should': [
                                {'terms': {'broadcast.master_id': ids}},
                                {'terms': {'broadcast.takes_package_id': ids}}
                            ]
                        }
                    }
                }
            }
        }

        req = ParsedRequest()
        req.args = {'source': json.dumps(query), 'repo': 'archive,published'}
        return get_resource_service('search').get(req=req, lookup=None)

    def get_broadcast_items_from_master_story(self, item):
        """
        Get the broadcast items from the master story.
        :param dict item: master story item
        :return list: returns list of broadcast items
        """
        if is_genre(item, BROADCAST_GENRE):
            return []

        ids = [str(item.get(config.ID_FIELD))]
        if self.takesService.get_take_package_id(item):
            ids.append(str(self.takesService.get_take_package_id(item)))

        return list(self._get_broadcast_items(ids))

    def on_broadcast_master_updated(self, item_event, item,
                                    takes_package_id=None, rewrite_id=None):
        """
        This event is called when the master story is corrected, published, re-written, new take/re-opened
        :param str item_event: Item operations
        :param dict item: item on which operation performed.
        :param str takes_package_id: takes_package_id.
        :param str rewrite_id: re-written story id.
        """
        status = ''

        if not item or is_genre(item, BROADCAST_GENRE):
            return

        if item_event == ITEM_CREATE and takes_package_id:
            status = 'New take created or story reopened.'
        elif item_event == ITEM_CREATE and rewrite_id:
            status = 'Master story re-written.'
        elif item_event == ITEM_PUBLISH:
            status = 'Master Story Published'
        elif item_event == ITEM_CORRECT:
            status = 'Master Story Corrected'

        broadcast_items = self.get_broadcast_items_from_master_story(item)

        if not broadcast_items:
            return

        processed_ids = set()
        for broadcast_item in broadcast_items:
            try:
                if broadcast_item.get('lock_user'):
                    continue

                updates = {
                    'broadcast': broadcast_item.get('broadcast'),
                }

                if status:
                    updates['broadcast']['status'] = status

                if not updates['broadcast']['takes_package_id'] and takes_package_id:
                    updates['broadcast']['takes_package_id'] = takes_package_id

                if not updates['broadcast']['rewrite_id'] and rewrite_id:
                    updates['broadcast']['rewrite_id'] = rewrite_id

                if not broadcast_item.get(config.ID_FIELD) in processed_ids:
                    self._update_broadcast_status(broadcast_item, updates)
                    # list of ids that are processed.
                    processed_ids.add(broadcast_item.get(config.ID_FIELD))
            except:
                logger.exception('Failed to update status for the broadcast item {}'.
                                 format(broadcast_item.get(config.ID_FIELD)))

    def _update_broadcast_status(self, item, updates):
        """
        Update the status of the broadcast item
        :param dict item: broadcast item to be updated
        :param dict updates: broadcast updates
        """
        # update the published collection as well as archive.
        if item.get(ITEM_STATE) in [CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED, CONTENT_STATE.KILLED]:
            get_resource_service('published').update_published_items(item.get(config.ID_FIELD),
                                                                     'broadcast', updates.get('broadcast'))

        archive_item = get_resource_service(SOURCE).find_one(req=None, _id=item.get(config.ID_FIELD))
        get_resource_service(SOURCE).system_update(archive_item.get(config.ID_FIELD), updates, archive_item)

    def remove_rewrite_refs(self, item):
        """
        Remove the rewrite references from the broadcast item if the re-write is spiked.
        :param dict item: Re-written article of the original story
        """
        if is_genre(item, BROADCAST_GENRE):
            return

        query = {
            'query': {
                'filtered': {
                    'filter': {
                        'and': [
                            {'term': {'genre.name': BROADCAST_GENRE}},
                            {'term': {'broadcast.rewrite_id': item.get(config.ID_FIELD)}}
                        ]
                    }
                }
            }
        }

        req = ParsedRequest()
        req.args = {'source': json.dumps(query)}
        broadcast_items = list(get_resource_service(SOURCE).get(req=req, lookup=None))

        if not broadcast_items:
            return

        for broadcast_item in broadcast_items:
            try:
                updates = {
                    'broadcast': broadcast_item.get('broadcast', {})
                }

                updates['broadcast']['rewrite_id'] = None

                if 're-written' in updates['broadcast']['status']:
                    updates['broadcast']['status'] = ''

                self._update_broadcast_status(broadcast_item, updates)
            except:
                logger.exception('Failed to remove rewrite id for the broadcast item {}'.
                                 format(broadcast_item.get(config.ID_FIELD)))

    def reset_broadcast_status(self, updates, original):
        """
        Reset the broadcast status if the broadcast item is updated.
        :param dict updates: updates to the original document
        :param dict original: original document
        """
        if original.get('broadcast') and original.get('broadcast').get('status', ''):
            broadcast_updates = {
                'broadcast': original.get('broadcast'),
            }

            broadcast_updates['broadcast']['status'] = ''
            self._update_broadcast_status(original, broadcast_updates)
            updates.update(broadcast_updates)

    def spike_item(self, original):
        """
        If Original item is re-write then it will remove the reference from the broadcast item.
        :param: dict original: original document
        """
        if original.get('rewrite_of'):
            self.remove_rewrite_refs(original)
