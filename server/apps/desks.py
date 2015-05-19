# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from superdesk.errors import SuperdeskApiError

from superdesk.resource import Resource
from bson.objectid import ObjectId
from superdesk.services import BaseService
import superdesk
from apps.tasks import default_status
from superdesk.notification import push_notification

desks_schema = {
    'name': {
        'type': 'string',
        'iunique': True,
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
    },
    'published_item_expiry': {
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

    def on_delete(self, desk):
        """
        Overriding to prevent deletion of a desk if the desk meets one of the below conditions:
            1. The desk isn't assigned as a default desk to user(s)
            2. The desk has no content
            3. The desk is associated with routing rule(s)
        """

        as_default_desk = superdesk.get_resource_service('users').get(req=None, lookup={'desk': desk['_id']})
        if as_default_desk and as_default_desk.count():
            raise SuperdeskApiError.preconditionFailedError(
                message='Cannot delete desk as it is assigned as default desk to user(s).')

        routing_rules_query = {'$or': [{'rules.actions.fetch.desk': desk['_id']},
                                       {'rules.actions.publish.desk': desk['_id']}]
                               }
        routing_rules = superdesk.get_resource_service('routing_schemes').get(req=None, lookup=routing_rules_query)
        if routing_rules and routing_rules.count():
            raise SuperdeskApiError.preconditionFailedError(
                message='Cannot delete desk as routing scheme(s) are associated with the desk')

        items = superdesk.get_resource_service('archive').get(req=None, lookup={'task.desk': str(desk['_id'])})
        if items and items.count():
            raise SuperdeskApiError.preconditionFailedError(message='Cannot delete desk as it has article(s).')

    def delete(self, lookup):
        """
        Overriding to delete stages before deleting a desk
        """

        superdesk.get_resource_service('stages').delete(lookup={'desk': lookup.get('_id')})
        super().delete(lookup)

    def on_deleted(self, doc):
        push_notification(self.notification_key, deleted=1, desk_id=str(doc.get('_id')))

    def on_updated(self, updates, original):
        push_notification(self.notification_key, updated=1, desk_id=str(original.get('_id')))


class UserDesksResource(Resource):
    url = 'users/<regex("[a-f0-9]{24}"):user_id>/desks'
    schema = desks_schema
    datasource = {'source': 'desks', 'default_sort': [('name', 1)]}
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
