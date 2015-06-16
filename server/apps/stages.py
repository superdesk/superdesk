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
from flask import current_app as app
from superdesk.notification import push_notification
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.errors import SuperdeskApiError
from superdesk import get_resource_service
from eve.utils import ParsedRequest
from apps.tasks import task_statuses
from superdesk.utc import get_expiry_date
from apps.common.models.utils import get_model
from apps.item_lock.models.item import ItemModel

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
            'minlength': 1,
            'iunique_per_parent': 'desk'
        },
        'description': {
            'type': 'string'
        },
        'default_incoming': {
            'type': 'boolean',
            'default': False
        },
        'task_status': {
            'type': 'string',
            'allowed': task_statuses,
            'required': True
        },
        'desk_order': {
            'type': 'integer',
            'readonly': True
        },
        'desk': Resource.rel('desks', embeddable=True, required=True),
        'content_expiry': {
            'type': 'integer'
        },
        'is_visible': {
            'type': 'boolean',
            'default': True
        },
        'incoming_macro': {
            'type': 'string'
        },
        'outgoing_macro': {
            'type': 'string'
        }
    }

    privileges = {'POST': 'desks', 'DELETE': 'desks', 'PATCH': 'desks'}


class StagesService(BaseService):
    notification_key = 'stage'

    def on_create(self, docs):
        for doc in docs:
            if not doc.get('desk'):
                doc['desk_order'] = 1
                continue
            req = ParsedRequest()
            req.sort = '-desk_order'
            req.max_results = 1
            prev_stage = self.get(req=req, lookup={'desk': doc['desk']})
            if doc.get('content_expiry', 0) == 0:
                doc['content_expiry'] = app.settings['CONTENT_EXPIRY_MINUTES']
            if prev_stage.count() == 0:
                doc['desk_order'] = 1
            else:
                doc['desk_order'] = prev_stage[0].get('desk_order', 1) + 1
            # if this new one is default need to remove the old default
            if doc.get('default_incoming', False):
                self.remove_old_default(doc.get('desk'), 'default_incoming')

    def on_created(self, docs):
        for doc in docs:
            if 'desk' in doc:
                push_notification(self.notification_key,
                                  created=1,
                                  stage_id=str(doc.get('_id')),
                                  desk_id=str(doc.get('desk')),
                                  is_visible=doc.get('is_visible', True))
            if doc.get('default_incoming', False):
                self.set_desk_ref(doc, 'incoming_stage')

    def on_delete(self, doc):
        if doc['default_incoming'] is True:
            desk_id = doc.get('desk', None)
            if desk_id and superdesk.get_resource_service('desks').find_one(req=None, _id=desk_id):
                raise SuperdeskApiError.forbiddenError(message='Cannot delete a default stage.')
        else:
            # check if the stage has any documents in it
            items = self.get_stage_documents(str(doc['_id']))
            if items.count() > 0:  # cannot delete
                raise SuperdeskApiError.forbiddenError(message='Only empty stages can be deleted.')

    def on_deleted(self, doc):
        push_notification(self.notification_key,
                          deleted=1,
                          stage_id=str(doc.get('_id')),
                          desk_id=str(doc.get('desk')))

    def on_update(self, updates, original):
        if updates.get('content_expiry') == 0:
            updates['content_expiry'] = app.settings['CONTENT_EXPIRY_MINUTES']
        super().on_update(updates, original)
        if updates.get('content_expiry', None):
            docs = self.get_stage_documents(str(original['_id']))
            for doc in docs:
                expiry = get_expiry_date(updates['content_expiry'], doc['versioncreated'])
                item_model = get_model(ItemModel)
                item_model.update({'_id': doc['_id']}, {'expiry': expiry})

        if updates.get('default_incoming', False):
            if not original.get('default_incoming'):
                self.remove_old_default(original.get('desk'), 'default_incoming')
                self.set_desk_ref(original, 'incoming_stage')
        else:
            if original.get('default_incoming') and 'default_incoming' in updates:
                raise SuperdeskApiError.forbiddenError(message='Must have one incoming stage in a desk')

    def on_updated(self, updates, original):
        if 'is_visible' in updates and updates['is_visible'] != original.get('is_visible', True):
            push_notification('stage_visibility_updated',
                              updated=1,
                              stage_id=str(original['_id']),
                              desk_id=str(original['desk']),
                              is_visible=updates.get('is_visible', original.get('is_visible', True)))
        else:
            push_notification(self.notification_key,
                              updated=1,
                              stage_id=str(original.get('_id')),
                              desk_id=str(original.get('desk')))

    def get_stage_documents(self, stage_id):
        query_filter = superdesk.json.dumps({'term': {'task.stage': stage_id}})
        req = ParsedRequest()
        req.args = {'filter': query_filter}
        return superdesk.get_resource_service('archive').get(req, None)

    def get_stages_by_visibility(self, is_visible=False, user_desk_ids=[]):
        """
        returns a list of stages for a user.
        """
        if is_visible:
            lookup = {'$or': [{'is_visible': True}]}
            if user_desk_ids:
                lookup['$or'].append({'desk': {'$in': user_desk_ids}})
        else:
            lookup = {'is_visible': False}
            if user_desk_ids:
                lookup['desk'] = {'$nin': user_desk_ids}

        return list(self.get(req=None, lookup=lookup))

    def set_desk_ref(self, doc, field):
        desk = get_resource_service('desks').find_one(_id=doc.get('desk'), req=None)
        if desk:
            get_resource_service('desks').update(doc.get('desk'), {field: doc.get('_id')}, desk)

    def clear_desk_ref(self, doc, field):
        desk = get_resource_service('desks').find_one(_id=doc.get('desk'), req=None)
        if desk:
            get_resource_service('desks').update(doc.get('desk'), {field: None}, desk)

    def remove_old_default(self, desk, field):
        lookup = {'$and': [{field: True}, {'desk': str(desk)}]}
        stages = self.get(req=None, lookup=lookup)
        for stage in stages:
            get_resource_service('stages').update(stage.get('_id'), {field: False}, stage)
