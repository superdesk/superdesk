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
from apps.archive.common import CUSTOM_HATEOAS, insert_into_versions, get_user
from apps.packages import TakesPackageService
from superdesk.resource import Resource, build_custom_hateoas
from superdesk.services import BaseService
from superdesk.metadata.utils import item_url
from superdesk.metadata.item import CONTENT_TYPE, CONTENT_STATE, ITEM_TYPE, ITEM_STATE
from superdesk.metadata.packages import RESIDREF
from superdesk import get_resource_service, config
from superdesk.errors import SuperdeskApiError
from apps.archive.archive import SOURCE


logger = logging.getLogger(__name__)
# field to be copied from item to broadcast item
FIELDS_TO_COPY = ['urgency', 'priority', 'anpa_category', 'type',
                  'subject', 'dateline', 'slugline', 'place']
ARCHIVE_BROADCAST_NAME = 'archive_broadcast'
BROADCAST_GENRE = 'Broadcast Script'


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
        broadcast_genre = [genre for genre in genre_list.get('items', []) if genre.get('value') == BROADCAST_GENRE]

        if not broadcast_genre:
            raise SuperdeskApiError.badRequestError(message="Cannot find the {} genre.".format(BROADCAST_GENRE))

        doc['broadcast'] = {
            'status': '',
            'master_id': item_id,
            'takes_package_id': self.takesService.get_take_package_id(item)
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
        Broadcast item can only be created for Text or Preformatted item.
        The state of the item cannot be Killed, Scheduled or Spiked
        :param dict item: item from which the broadcast item will be created
        """
        # TODO: for takes package only one broadcast content is allowed

        if not item:
            raise SuperdeskApiError.notFoundError(
                message="Cannot find the requested item id.")

        if not item.get(ITEM_TYPE) in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]:
            raise SuperdeskApiError.badRequestError(message="Invalid content type.")

        if item.get(ITEM_STATE) in [CONTENT_STATE.KILLED, CONTENT_STATE.SCHEDULED, CONTENT_STATE.SPIKED]:
            raise SuperdeskApiError.badRequestError(message="Invalid content state.")

        takes_package = self.takesService.get_take_package(item)

        if not takes_package:
            return

        refs = self.takesService.get_package_refs(takes_package)
        broadcast_items = self._get_broadcast_items(
            [{config.ID_FIELD: ref.get(RESIDREF), ITEM_TYPE: CONTENT_TYPE.TEXT} for ref in refs])

        if broadcast_items.count() != 0:
            raise SuperdeskApiError.badRequestError(message='Takes already have broadcast content associated with it.')

    def is_broadcast(self, item):
        """
        Item to check if broadcast or not.
        :param dict item:
        :return: If broadcast then true else false
        """
        return item.get('genre') and any(genre.get('value') == BROADCAST_GENRE for genre in item.get('genre', []))

    def _get_broadcast_items(self, items):
        """

        :param list items: list of items
        :return list: list of broadcast items
        """
        ids = [str(item.get(config.ID_FIELD)) for item in items
               if item.get(ITEM_TYPE) in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]]

        query = {
            'query': {
                'filtered': {
                    'filter': {
                        'and': [
                            {'terms': {'broadcast.master_id': ids}},
                            {'term': {'genre.name': BROADCAST_GENRE}}
                        ]
                    }
                }
            }
        }

        request = ParsedRequest()
        request.args = {'source': json.dumps(query)}
        broadcast_items = get_resource_service(SOURCE).get(req=request, lookup=None) or []
        return broadcast_items

    def enhance_items(self, items):
        """
        Sets the broadcast_id attribute if master story has broadcast script
        :param list items: list of items
        """
        broadcast_items = self._get_broadcast_items(items)

        for broadcast_item in broadcast_items:
            item = next((item for item in items
                         if item.get(config.ID_FIELD) == broadcast_item.get('broadcast', {}).get('master_id')), None)
            if item:
                item['broadcast_id'] = broadcast_item.get(config.ID_FIELD)

            item = next((item for item in items
                         if not item.get('broadcast_id') and
                         self.takesService.get_take_package_id(item) ==
                         broadcast_item.get('broadcast', {}).get('takes_package_id')), None)

            if item:
                item['broadcast_id'] = broadcast_item.get(config.ID_FIELD)

    def get_broadcast_story_from_master_story(self, item):
        """
        Get the broadcast story from the master story.
        :param dict item: master story item
        :return dict: return broadcast story if found else None
        """

        if self.is_broadcast(item):
            return None

        broadcast_items = list(self._get_broadcast_items([item]))
        return broadcast_items[0] if broadcast_items else None

    def on_takes_package_created(self, take_package_id, item):
        """
        This event will be called on takes package creation
        :param str take_package_id:
        :param dict item:
        """
        broadcast_items = list(self._get_broadcast_items([item]))
        if not broadcast_items:
            return

        broadcast_item = broadcast_items[0]
        if broadcast_item.get('broadcast', {}).get('takes_package_id'):
            return

        updates = {
            'broadcast': broadcast_item.get('broadcast')
        }
        updates['broadcast']['takes_package_id'] = take_package_id
        get_resource_service(SOURCE).system_update(broadcast_item[config.ID_FIELD], updates, broadcast_item)
