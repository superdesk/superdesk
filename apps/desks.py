from superdesk.models import BaseModel
from bson.objectid import ObjectId


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
    DesksModel(app=app)
    UserDesksModel(app=app)


class DesksModel(BaseModel):
    endpoint_name = 'desks'
    schema = desks_schema
    datasource = {'default_sort': [('created', -1)]}


class UserDesksModel(BaseModel):
    endpoint_name = 'user_desks'
    url = 'users/<regex("[a-f0-9]{24}"):user_id>/desks'
    schema = desks_schema
    datasource = {'source': 'desks'}
    resource_methods = ['GET']

    def get(self, req, lookup):
        if lookup.get('user_id'):
            lookup["members.user"] = ObjectId(lookup['user_id'])
            del lookup['user_id']
        return super().get(req, lookup)
