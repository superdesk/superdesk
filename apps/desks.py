from superdesk.resource import Resource
from bson.objectid import ObjectId
from superdesk.services import BaseService
import superdesk

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
    'incoming_stage': Resource.rel('stages', True)
}


def init_app(app):
    endpoint_name = 'desks'
    service = DesksService(endpoint_name, backend=superdesk.get_backend())
    DesksResource(endpoint_name, app=app, service=service)
    endpoint_name = 'user_desks'
    service = UserDesksService(endpoint_name, backend=superdesk.get_backend())
    UserDesksResource(endpoint_name, app=app, service=service)


class DesksResource(Resource):
    schema = desks_schema
    datasource = {'default_sort': [('created', -1)]}


class DesksService(BaseService):

    def create(self, docs, **kwargs):
        for doc in docs:
            if not doc.get('incoming_stage', None):
                stage = {'name': 'New', 'default_incoming': True}
                superdesk.get_resource_service('stages').post([stage])
                doc['incoming_stage'] = stage.get('_id')
                super().create([doc], **kwargs)
                superdesk.get_resource_service('stages').patch(doc['incoming_stage'], {'desk': doc['_id']})
            else:
                super().create([doc], **kwargs)
        return [doc['_id'] for doc in docs]


class UserDesksResource(Resource):
    url = 'users/<regex("[a-f0-9]{24}"):user_id>/desks'
    schema = desks_schema
    datasource = {'source': 'desks'}
    resource_methods = ['GET']


class UserDesksService(BaseService):

    def get(self, req, lookup):
        if lookup.get('user_id'):
            lookup["members.user"] = ObjectId(lookup['user_id'])
            del lookup['user_id']
        return super().get(req, lookup)
