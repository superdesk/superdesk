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
from superdesk import config
from superdesk.utils import SuperdeskBaseEnum
from bson.objectid import ObjectId
from superdesk.services import BaseService
import superdesk
from apps.tasks import default_status
from superdesk.notification import push_notification
from superdesk.activity import add_activity, ACTIVITY_UPDATE


class DeskTypes(SuperdeskBaseEnum):
    authoring = 'authoring'
    production = 'production'


desks_schema = {
    'name': {
        'type': 'string',
        'required': True,
        'nullable': False,
        'empty': False,
        'iunique': True
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
    'source': {
        'type': 'string'
    },
    'published_item_expiry': {
        'type': 'integer'
    },
    'monitoring_settings': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                '_id': {
                    'type': 'string',
                    'required': True
                },
                'type': {
                    'type': 'string',
                    'allowed': ['search', 'stage', 'personal'],
                    'required': True
                },
                'max_items': {
                    'type': 'integer',
                    'required': True
                }
            }
        }
    },
    'desk_type': {
        'type': 'string',
        'default': DeskTypes.authoring.value,
        'allowed': DeskTypes.values()
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
    privileges = {'POST': 'desks', 'PATCH': 'desks', 'DELETE': 'desks'}


class DesksService(BaseService):
    notification_key = 'desk'

    def create(self, docs, **kwargs):
        for doc in docs:
            doc.setdefault('desk_type', DeskTypes.authoring.value)
            if not doc.get('incoming_stage', None):
                stage = {'name': 'New', 'default_incoming': True, 'desk_order': 1, 'task_status': default_status}
                superdesk.get_resource_service('stages').post([stage])
                doc['incoming_stage'] = stage.get(config.ID_FIELD)
                super().create([doc], **kwargs)
                superdesk.get_resource_service('stages').patch(doc['incoming_stage'], {'desk': doc[config.ID_FIELD]})
            else:
                super().create([doc], **kwargs)
        return [doc[config.ID_FIELD] for doc in docs]

    def on_created(self, docs):
        for doc in docs:
            push_notification(self.notification_key, created=1, desk_id=str(doc.get(config.ID_FIELD)))

    def on_update(self, updates, original):
        if updates.get('desk_type') and updates.get('desk_type') != original.get('desk_type', ''):
            archive_versions_query = {
                '$or': [
                    {'task.last_authoring_desk': str(original[config.ID_FIELD])},
                    {'task.last_production_desk': str(original[config.ID_FIELD])}
                ]
            }

            items = superdesk.get_resource_service('archive_versions').get(req=None, lookup=archive_versions_query)
            if items and items.count():
                raise SuperdeskApiError.badRequestError(
                    message='Cannot update Desk Type as there are article(s) referenced by the Desk.')

    def on_delete(self, desk):
        """
        Overriding to prevent deletion of a desk if the desk meets one of the below conditions:
            1. The desk isn't assigned as a default desk to user(s)
            2. The desk has no content
            3. The desk is associated with routing rule(s)
        """

        as_default_desk = superdesk.get_resource_service('users').get(req=None, lookup={'desk': desk[config.ID_FIELD]})
        if as_default_desk and as_default_desk.count():
            raise SuperdeskApiError.preconditionFailedError(
                message='Cannot delete desk as it is assigned as default desk to user(s).')

        routing_rules_query = {
            '$or': [
                {'rules.actions.fetch.desk': desk[config.ID_FIELD]},
                {'rules.actions.publish.desk': desk[config.ID_FIELD]}
            ]
        }
        routing_rules = superdesk.get_resource_service('routing_schemes').get(req=None, lookup=routing_rules_query)
        if routing_rules and routing_rules.count():
            raise SuperdeskApiError.preconditionFailedError(
                message='Cannot delete desk as routing scheme(s) are associated with the desk')

        archive_versions_query = {
            '$or': [
                {'task.desk': str(desk[config.ID_FIELD])},
                {'task.last_authoring_desk': str(desk[config.ID_FIELD])},
                {'task.last_production_desk': str(desk[config.ID_FIELD])}
            ]
        }

        items = superdesk.get_resource_service('archive_versions').get(req=None, lookup=archive_versions_query)
        if items and items.count():
            raise SuperdeskApiError.preconditionFailedError(
                message='Cannot delete desk as it has article(s) or referenced by versions of the article(s).')

    def delete(self, lookup):
        """
        Overriding to delete stages before deleting a desk
        """

        superdesk.get_resource_service('stages').delete(lookup={'desk': lookup.get(config.ID_FIELD)})
        super().delete(lookup)

    def on_deleted(self, doc):
        desk_user_ids = [str(member['user']) for member in doc.get('members', [])]
        push_notification(self.notification_key,
                          deleted=1,
                          user_ids=desk_user_ids,
                          desk_id=str(doc.get(config.ID_FIELD)))

    def on_updated(self, updates, original):
        self.__send_notification(updates, original)

    def __compare_members(self, original, updates):
        original_members = set([member['user'] for member in original])
        updates_members = set([member['user'] for member in updates])
        added = updates_members - original_members
        removed = original_members - updates_members
        return added, removed

    def __send_notification(self, updates, desk):
        desk_id = desk[config.ID_FIELD]

        if 'members' in updates:
            added, removed = self.__compare_members(desk.get('members', {}), updates['members'])
            if len(removed) > 0:
                push_notification('desk_membership_revoked',
                                  updated=1,
                                  user_ids=[str(item) for item in removed],
                                  desk_id=str(desk_id))

            for added_user in added:
                user = superdesk.get_resource_service('users').find_one(req=None, _id=added_user)
                add_activity(ACTIVITY_UPDATE,
                             'user {{user}} has been added to desk {{desk}}: Please re-login.',
                             self.datasource,
                             notify=added,
                             user=user.get('username'),
                             desk=desk.get('name'))
        else:
            push_notification(self.notification_key, updated=1, desk_id=str(desk.get(config.ID_FIELD)))


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
