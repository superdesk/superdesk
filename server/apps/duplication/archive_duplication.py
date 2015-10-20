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
from apps.content import push_content_notification
from apps.tasks import send_to

from superdesk import get_resource_service
import superdesk
from superdesk.errors import SuperdeskApiError, InvalidStateTransitionError
from superdesk.metadata.item import CONTENT_STATE, ITEM_STATE
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.metadata.utils import item_url
from apps.archive.archive import SOURCE as ARCHIVE
from superdesk.workflow import is_workflow_state_transition_valid


class DuplicateResource(Resource):
    endpoint_name = 'duplicate'
    resource_title = endpoint_name

    schema = {
        'desk': Resource.rel('desks', False, required=True)
    }

    url = 'archive/<{0}:guid>/duplicate'.format(item_url)

    resource_methods = ['POST']
    item_methods = []

    privileges = {'POST': 'duplicate'}


class DuplicateService(BaseService):
    def create(self, docs, **kwargs):
        guid_of_item_to_be_duplicated = request.view_args['guid']

        guid_of_duplicated_items = []

        for doc in docs:
            archive_service = get_resource_service(ARCHIVE)

            archived_doc = archive_service.find_one(req=None, _id=guid_of_item_to_be_duplicated)
            if not archived_doc:
                raise SuperdeskApiError.notFoundError('Fail to found item with guid: %s' %
                                                      guid_of_item_to_be_duplicated)

            current_desk_of_item = archived_doc.get('task', {}).get('desk')
            if current_desk_of_item is None or str(current_desk_of_item) != str(doc.get('desk')):
                raise SuperdeskApiError.preconditionFailedError(message='Duplicate is allowed within the same desk.')

            if not is_workflow_state_transition_valid('duplicate', archived_doc[ITEM_STATE]):
                raise InvalidStateTransitionError()

            send_to(doc=archived_doc, desk_id=doc.get('desk'))
            new_guid = archive_service.duplicate_content(archived_doc)
            guid_of_duplicated_items.append(new_guid)

        if kwargs.get('notify', True):
            push_content_notification([archived_doc])

        return guid_of_duplicated_items


superdesk.workflow_action(
    name='duplicate',
    exclude_states=[CONTENT_STATE.SPIKED, CONTENT_STATE.KILLED],
    privileges=['archive', 'duplicate']
)
