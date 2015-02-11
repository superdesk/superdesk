# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.resource import Resource
from bson.objectid import ObjectId
from superdesk.services import BaseService
import superdesk
from apps.tasks import default_status
from superdesk.notification import push_notification

desks_schema = {
    'name': {
        'type': 'string',
        'unique': True,
        'required': True,
    },
    'description': {
        'type': 'string'
    },
    'members': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'user': Resource.rel('users', True)
            }
        }
    },
    'incoming_stage': Resource.rel('stages', True),
    'spike_expiry': {
        'type': 'integer'
    }
}


def init_app(app):
    endpoint_name = 'desks'
    service = DesksService(endpoint_name, backend=superdesk.get_backend())
    DesksResource(endpoint_name, app=app, service=service)
    endpoint_name = 'user_desks'
    service = UserDesksService(endpoint_name, backend=superdesk.get_backend())
    UserDesksResource(endpoint_name, app=app, service=service)


superdesk.privilege(name='desks', label='Desk Management', description='User can manage desks.')


class DesksResource(Resource):
    schema = desks_schema
    datasource = {'default_sort': [('created', -1)]}
    privileges = {'POST': 'desks', 'PATCH': 'desks', 'DELETE': 'desks'}


class DesksService(BaseService):
    notification_key = 'desk'

    def create(self, docs, **kwargs):
        for doc in docs:
            if not doc.get('incoming_stage', None):
                stage = {'name': 'New', 'default_incoming': True, 'desk_order': 1, 'task_status': default_status}
                superdesk.get_resource_service('stages').post([stage])
                doc['incoming_stage'] = stage.get('_id')
                super().create([doc], **kwargs)
                superdesk.get_resource_service('stages').patch(doc['incoming_stage'], {'desk': doc['_id']})
            else:
                super().create([doc], **kwargs)
        return [doc['_id'] for doc in docs]

    def on_created(self, docs):
        for doc in docs:
            push_notification(self.notification_key, created=1, desk_id=str(doc.get('_id')))

    def on_deleted(self, doc):
        push_notification(self.notification_key, deleted=1, desk_id=str(doc.get('_id')))

    def on_updated(self, updates, original):
        push_notification(self.notification_key, updated=1, desk_id=str(original.get('_id')))


class UserDesksResource(Resource):
    url = 'users/<regex("[a-f0-9]{24}"):user_id>/desks'
    schema = desks_schema
    datasource = {'source': 'desks'}
    resource_methods = ['GET']


class UserDesksService(BaseService):

    def get(self, req, lookup):
        if lookup.get('user_id'):
            lookup['members.user'] = ObjectId(lookup['user_id'])
            del lookup['user_id']
        return super().get(req, lookup)

    def is_member(self, user_id, desk_id):
        # desk = list(self.get(req=None, lookup={'members.user':ObjectId(user_id), '_id': ObjectId(desk_id)}))
        return len(list(self.get(req=None, lookup={'members.user': ObjectId(user_id), '_id': ObjectId(desk_id)}))) > 0
