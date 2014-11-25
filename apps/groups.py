from superdesk.resource import Resource
from superdesk.services import BaseService
from bson.objectid import ObjectId
import superdesk


def init_app(app):
    endpoint_name = 'groups'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    GroupsResource(endpoint_name, app=app, service=service)
    endpoint_name = 'user_groups'
    service = UserGroupsService(endpoint_name, backend=superdesk.get_backend())
    UserGroupsResource(endpoint_name, app=app, service=service)


superdesk.privilege(name='groups', label='Groups Management', description='User can edit unique name.')


class GroupsResource(Resource):

    schema = {
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
        }
    }
    datasource = {'default_sort': [('created', -1)]}
    privileges = {'POST': 'groups', 'DELETE': 'groups', 'PATCH': 'groups'}


class UserGroupsResource(Resource):
    url = 'users/<regex("[a-f0-9]{24}"):user_id>/groups'
    schema = GroupsResource.schema
    datasource = {'source': 'groups'}
    resource_methods = ['GET']


class UserGroupsService(BaseService):

    def get(self, req, lookup):
        if lookup.get('user_id'):
            lookup["members.user"] = ObjectId(lookup['user_id'])
            del lookup['user_id']
        return super().get(req, lookup)
