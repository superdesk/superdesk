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
from flask import request
from apps.archive.common import CUSTOM_HATEOAS
from superdesk.resource import Resource, build_custom_hateoas
from superdesk.services import BaseService
from superdesk.metadata.utils import item_url
from superdesk.metadata.item import CONTENT_TYPE, CONTENT_STATE, ITEM_TYPE, ITEM_STATE
from superdesk import get_resource_service, config
from superdesk.errors import SuperdeskApiError
from apps.archive.archive import SOURCE


logger = logging.getLogger(__name__)
# field to be copied from item to broadcast item
FIELDS_TO_COPY = ['urgency', 'priority', 'anpa_category', 'type',
                  'subject', 'dateline', 'slugline', 'place']
ARCHIVE_BROADCAST_NAME = 'archive_broadcast'


class ArchiveBroadcastResource(Resource):
    endpoint_name = ARCHIVE_BROADCAST_NAME
    resource_title = endpoint_name

    url = 'archive/<{0}:item_id>/broadcast'.format(item_url)

    resource_methods = ['POST']
    item_methods = []
    privileges = {'POST': ARCHIVE_BROADCAST_NAME}


class ArchiveBroadcastService(BaseService):

    def create(self, docs):
        service = get_resource_service(SOURCE)
        item_id = request.view_args['item_id']
        item = service.find_one(req=None, _id=item_id)

        genre_list = get_resource_service('vocabularies').find_one(req=None, _id='genre')
        broadcast_genre = [genre for genre in genre_list.items if genre.value.lower() == 'broadcast script']

        if not broadcast_genre:
            raise SuperdeskApiError.badRequestError(message="Cannot find the Broadcast Script genere.")

        broadcast_item = {
            'broadcast': {
                'status': ''
            },
            'genre': broadcast_genre
        }

        for key in FIELDS_TO_COPY:
            broadcast_item[key] = item.get(key)

        broadcast_item['family_id'] = item_id
        service.post([broadcast_item])
        build_custom_hateoas(CUSTOM_HATEOAS, broadcast_item)
        docs = [broadcast_item]
        return [broadcast_item[config.ID_FIELD]]

    def _valid_broadcast_item(self, item):
        """
        Broadcast item can only be created for Text or Preformatted item.
        The state of the item cannot be Killed, Scheduled or Spiked
        :param dict item: item from which the broadcast item will be created
        """
        if not item:
            raise SuperdeskApiError.notFoundError(
                message="Cannot find the item with id: {}".format(item.get(config.ID_FIELD)))

        if not item.get(ITEM_TYPE) in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]:
            raise SuperdeskApiError.badRequestError(message="Invalid content type.")

        if item.get(ITEM_STATE) in [CONTENT_STATE.KILLED, CONTENT_STATE.SCHEDULED, CONTENT_STATE.SPIKED]:
            raise SuperdeskApiError.badRequestError(message="Invalid content state.")
