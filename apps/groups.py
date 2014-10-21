from superdesk.resource import Resource
from superdesk.services import BaseService
import superdesk


def init_app(app):
    endpoint_name = 'groups'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    GroupsResource(endpoint_name, app=app, service=service)


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
