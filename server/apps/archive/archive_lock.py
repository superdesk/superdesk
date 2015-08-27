# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from flask import request
from superdesk.resource import Resource, build_custom_hateoas
from superdesk.metadata.utils import item_url
from .common import get_user, get_auth, CUSTOM_HATEOAS
from superdesk.services import BaseService
from apps.common.components.utils import get_component
from apps.item_lock.components.item_lock import ItemLock


def _update_returned_document(doc, item):
    doc.clear()
    doc.update(item)
    build_custom_hateoas(CUSTOM_HATEOAS, doc)
    return [doc['_id']]


class ArchiveLockResource(Resource):
    endpoint_name = 'archive_lock'
    url = 'archive/<{0}:item_id>/lock'.format(item_url)
    schema = {'lock_user': {'type': 'string'}}
    datasource = {'source': 'archive'}
    resource_methods = ['GET', 'POST']
    resource_title = endpoint_name
    privileges = {'POST': 'archive'}


class ArchiveLockService(BaseService):

    def create(self, docs, **kwargs):
        user = get_user(required=True)
        auth = get_auth()
        item_id = request.view_args['item_id']
        item = get_component(ItemLock).lock({'_id': item_id}, user['_id'], auth['_id'], None)
        return _update_returned_document(docs[0], item)


class ArchiveUnlockResource(Resource):
    endpoint_name = 'archive_unlock'
    url = 'archive/<{0}:item_id>/unlock'.format(item_url)
    schema = {'lock_user': {'type': 'string'}}
    datasource = {'source': 'archive'}
    resource_methods = ['GET', 'POST']
    resource_title = endpoint_name


class ArchiveUnlockService(BaseService):

    def create(self, docs, **kwargs):
        user = get_user(required=True)
        auth = get_auth()
        item_id = request.view_args['item_id']
        item = get_component(ItemLock).unlock({'_id': item_id}, user['_id'], auth['_id'], None)

        if item is None:
            # version 1 item must have been deleted by now
            return [0]

        return _update_returned_document(docs[0], item)
