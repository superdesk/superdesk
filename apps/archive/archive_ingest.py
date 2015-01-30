# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""
Created on May 23, 2014

@author: Ioan v. Pocol
"""

import superdesk

from eve.utils import config
from apps.archive.common import insert_into_versions, remove_unwanted, set_original_creator
from apps.tasks import send_to

from superdesk.errors import SuperdeskApiError, InvalidStateTransitionError
from superdesk.utc import utcnow
from superdesk.resource import Resource
from superdesk.services import BaseService
from .archive import SOURCE as ARCHIVE
from superdesk.workflow import is_workflow_state_transition_valid
STATE_FETCHED = 'fetched'


class ArchiveIngestResource(Resource):
    resource_methods = ['POST']
    item_methods = []
    schema = {
        'guid': {'type': 'string', 'required': True},
        'desk': Resource.rel('desks', False, nullable=True)
    }
    privileges = {'POST': 'ingest_move'}


class ArchiveIngestService(BaseService):

    def create(self, docs, **kwargs):
        for doc in docs:
            ingest_doc = superdesk.get_resource_service('ingest').find_one(req=None, _id=doc.get('guid'))
            if not ingest_doc:
                msg = 'Fail to found ingest item with guid: %s' % doc.get('guid')
                raise SuperdeskApiError.notFoundError(msg)

            if not is_workflow_state_transition_valid('fetch_as_from_ingest', ingest_doc[config.CONTENT_STATE]):
                raise InvalidStateTransitionError()

            superdesk.get_resource_service('ingest').patch(ingest_doc.get('_id'), {'archived': utcnow()})

            archived_doc = superdesk.get_resource_service(ARCHIVE).find_one(req=None, _id=doc.get('guid'))
            if not archived_doc:
                dest_doc = dict(ingest_doc)
                dest_doc[config.VERSION] = 1
                dest_doc[config.CONTENT_STATE] = STATE_FETCHED
                send_to(dest_doc, dest_doc.get('desk'))
                dest_doc['created'] = dest_doc['firstcreated']
                dest_doc['updated'] = dest_doc['versioncreated']
                remove_unwanted(dest_doc)
                for ref in [ref for group in dest_doc.get('groups', [])
                            for ref in group.get('refs', []) if 'residRef' in ref]:
                    ref['location'] = ARCHIVE
                    ref['guid'] = ref['residRef']

                set_original_creator(dest_doc)
                superdesk.get_resource_service(ARCHIVE).post([dest_doc])
                insert_into_versions(dest_doc.get('guid'))
                desk = doc.get('desk')
                refs = [{'guid': ref.get('residRef'), 'desk': desk}
                        for group in dest_doc.get('groups', [])
                        for ref in group.get('refs', []) if 'residRef' in ref]
                if refs:
                    self.create(refs)

        return [doc.get('guid') for doc in docs]


superdesk.workflow_state(STATE_FETCHED)

superdesk.workflow_action(
    name='fetch_as_from_ingest',
    include_states=['ingested'],
    privileges=['archive', 'ingest_move']
)

superdesk.workflow_state('routed')
superdesk.workflow_action(
    name='route',
    include_states=['ingested']
)
