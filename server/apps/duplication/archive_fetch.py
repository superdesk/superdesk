# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from eve.utils import config
from flask import request
from apps.tasks import send_to

import superdesk

from apps.archive.archive import SOURCE as ARCHIVE
from apps.archive.common import item_url, generate_guid, GUID_TAG, generate_unique_id_and_name, INGEST_ID, FAMILY_ID, \
    remove_unwanted, set_original_creator, insert_into_versions, ITEM_OPERATION,\
    item_operations
from superdesk.errors import SuperdeskApiError, InvalidStateTransitionError
from superdesk.notification import push_notification
from superdesk.resource import Resource, build_custom_hateoas
from superdesk.services import BaseService
from superdesk.utc import utcnow
from superdesk.workflow import is_workflow_state_transition_valid
from superdesk import get_resource_service

custom_hateoas = {'self': {'title': 'Archive', 'href': '/archive/{_id}'}}
STATE_FETCHED = 'fetched'
ITEM_FETCH = 'fetch'
item_operations.extend([ITEM_FETCH])


class FetchResource(Resource):
    endpoint_name = 'fetch'
    resource_title = endpoint_name

    schema = {
        'desk': Resource.rel('desks', False, required=True),
        'stage': Resource.rel('stages', False, nullable=True),
        'macro': {'type': 'string'}
    }

    url = 'ingest/<{0}:id>/fetch'.format(item_url)

    resource_methods = ['POST']
    item_methods = []

    privileges = {'POST': 'fetch'}


class FetchService(BaseService):

    def create(self, docs, **kwargs):
        return self.fetch(docs, id=request.view_args.get('id'), **kwargs)

    def fetch(self, docs, id=None, **kwargs):
        id_of_fetched_items = []

        for doc in docs:
            id_of_item_to_be_fetched = doc.get('_id') if id is None else id

            desk_id = doc.get('desk')
            stage_id = doc.get('stage')

            ingest_service = get_resource_service('ingest')
            ingest_doc = ingest_service.find_one(req=None, _id=id_of_item_to_be_fetched)

            if not ingest_doc:
                raise SuperdeskApiError.notFoundError('Fail to found ingest item with _id: %s' %
                                                      id_of_item_to_be_fetched)

            if not is_workflow_state_transition_valid('fetch_from_ingest', ingest_doc[config.CONTENT_STATE]):
                raise InvalidStateTransitionError()

            if doc.get('macro'):  # there is a macro so transform it
                ingest_doc = get_resource_service('macros').execute_macro(ingest_doc, doc.get('macro'))

            archived = utcnow()
            ingest_service.patch(id_of_item_to_be_fetched, {'archived': archived})

            dest_doc = dict(ingest_doc)
            new_id = generate_guid(type=GUID_TAG)
            id_of_fetched_items.append(new_id)
            dest_doc['_id'] = new_id
            dest_doc['guid'] = new_id
            generate_unique_id_and_name(dest_doc)

            dest_doc[config.VERSION] = 1
            send_to(doc=dest_doc, desk_id=desk_id, stage_id=stage_id)
            dest_doc[config.CONTENT_STATE] = doc.get('state', STATE_FETCHED)
            dest_doc[INGEST_ID] = dest_doc[FAMILY_ID] = ingest_doc['_id']
            dest_doc[ITEM_OPERATION] = ITEM_FETCH

            remove_unwanted(dest_doc)
            set_original_creator(dest_doc)
            self.__fetch_items_in_package(dest_doc, desk_id, stage_id,
                                          doc.get('state', STATE_FETCHED))

            get_resource_service(ARCHIVE).post([dest_doc])
            insert_into_versions(doc=dest_doc)
            build_custom_hateoas(custom_hateoas, dest_doc)
            doc.update(dest_doc)

        if kwargs.get('notify', True):
            push_notification('item:fetch', fetched=1)

        return id_of_fetched_items

    def __fetch_items_in_package(self, dest_doc, desk, stage, state):
        for ref in [ref for group in dest_doc.get('groups', [])
                    for ref in group.get('refs', []) if 'residRef' in ref]:
            ref['location'] = ARCHIVE

        refs = [{'_id': ref.get('residRef'), 'desk': desk,
                 'stage': stage, 'state': state}
                for group in dest_doc.get('groups', [])
                for ref in group.get('refs', []) if 'residRef' in ref]

        if refs:
            new_ref_guids = self.fetch(refs, id=None, notify=False)
            count = 0
            for ref in [ref for group in dest_doc.get('groups', [])
                        for ref in group.get('refs', []) if 'residRef' in ref]:
                ref['residRef'] = ref['guid'] = new_ref_guids[count]
                count += 1


superdesk.workflow_state(STATE_FETCHED)
superdesk.workflow_action(
    name='fetch_from_ingest',
    include_states=['ingested'],
    privileges=['ingest', 'archive', 'fetch']
)

superdesk.workflow_state('routed')
superdesk.workflow_action(
    name='route',
    include_states=['ingested']
)
