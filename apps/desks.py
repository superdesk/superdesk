from superdesk.models import BaseModel
from bson.objectid import ObjectId
from superdesk.services import BaseService
import superdesk

desks_schema = {
    'name': {
        'type': 'string',
        'unique': True,
        'required': True,
    },
    'members': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'user': BaseModel.rel('users', True)
            }
        }
    }
}


def init_app(app):
    endpoint_name = 'desks'
    service = BaseService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    DesksModel(endpoint_name=endpoint_name, app=app, service=service)
    endpoint_name = 'user_desks'
    service = UserDesksService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    UserDesksModel(endpoint_name=endpoint_name, app=app, service=service)


class DesksModel(BaseModel):
    schema = desks_schema
    datasource = {'default_sort': [('created', -1)]}


class UserDesksModel(BaseModel):
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
