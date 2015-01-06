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
import superdesk
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.errors import SuperdeskApiError
from eve.utils import ParsedRequest
from apps.tasks import task_statuses


logger = logging.getLogger(__name__)


def init_app(app):
    endpoint_name = 'stages'
    service = StagesService(endpoint_name, backend=superdesk.get_backend())
    StagesResource(endpoint_name, app=app, service=service)


class StagesResource(Resource):
    schema = {
        'name': {
            'type': 'string',
            'required': True,
            'minlength': 1
        },
        'description': {
            'type': 'string',
            'minlength': 1
        },
        'default_incoming': {
            'type': 'boolean',
            'required': True,
            'default': False
        },
        'task_status': {
            'type': 'string',
            'allowed': task_statuses
        },
        'desk': Resource.rel('desks', embeddable=True),
        'content_expiry': {
            'type': 'integer'
        },
        'outgoing': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'stage': Resource.rel('stages', True)
                }
            }
        }
    }

    privileges = {'POST': 'desks', 'DELETE': 'desks', 'PATCH': 'desks'}


class StagesService(BaseService):

    def on_delete(self, doc):
        if doc['default_incoming'] is True:
            desk_id = doc.get('desk', None)
            if desk_id:
                desk = superdesk.get_resource_service('desks').find_one(req=None, _id=desk_id)
                if desk:
                    raise SuperdeskApiError.forbiddenError(message='Deleting default stages is not allowed.')
        else:
            # check if the stage has any documents in it
            items = self.get_stage_documents(str(doc['_id']))
            if items.count() > 0:
                # cannot delete
                raise SuperdeskApiError.forbiddenError(message='Only empty stages can be deleted.')

    def get_stage_documents(self, stage_id):
        query_filter = superdesk.json.dumps({'term': {'task.stage': stage_id}})
        req = ParsedRequest()
        req.args = {'filter': query_filter}
        return superdesk.get_resource_service('archive').get(req, None)
