# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from eve.versioning import resolve_document_version

import superdesk

from flask import request
from apps.tasks import send_to

from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError, InvalidStateTransitionError
from superdesk.resource import Resource
from superdesk.services import BaseService
from apps.archive.common import item_url, insert_into_versions
from apps.archive.archive import SOURCE as ARCHIVE
from superdesk.workflow import is_workflow_state_transition_valid
from eve.utils import config


class MoveResource(Resource):
    endpoint_name = 'move'
    resource_title = endpoint_name

    schema = {
        'desk': Resource.rel('desks', False, required=True),
        'stage': Resource.rel('stages', False, required=True)
    }

    url = 'archive/<{0}:guid>/move'.format(item_url)

    resource_methods = ['POST']
    item_methods = []

    privileges = {'POST': 'move'}


class MoveService(BaseService):
    def create(self, docs, **kwargs):
        guid_of_item_to_be_moved = request.view_args['guid']

        guid_of_moved_items = []

        for doc in docs:
            archive_service = get_resource_service(ARCHIVE)

            archived_doc = archive_service.find_one(req=None, _id=guid_of_item_to_be_moved)
            if not archived_doc:
                raise SuperdeskApiError.notFoundError('Fail to found item with guid: %s' %
                                                      guid_of_item_to_be_moved)

            current_desk_of_item = archived_doc.get('task', {}).get('desk')
            if current_desk_of_item and str(current_desk_of_item) == str(doc.get('desk')):
                raise SuperdeskApiError.preconditionFailedError(message='Move is not allowed within the same desk.')

            if not is_workflow_state_transition_valid('submit_to_desk', archived_doc[config.CONTENT_STATE]):
                raise InvalidStateTransitionError()

            original = dict(archived_doc)

            send_to(archived_doc, doc.get('desk'), doc.get('stage'))
            archived_doc[config.CONTENT_STATE] = 'submitted'
            resolve_document_version(archived_doc, ARCHIVE, 'PATCH', original)

            archive_service.update(archived_doc['_id'], archived_doc, original)

            insert_into_versions(doc=archived_doc)

            guid_of_moved_items.append(archived_doc['guid'])

        return guid_of_moved_items


superdesk.workflow_action(
    name='submit_to_desk',
    include_states=['draft', 'fetched', 'routed', 'submitted', 'in_progress'],
    privileges=['archive', 'move']
)
