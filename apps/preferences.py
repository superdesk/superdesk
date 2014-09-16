from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk import get_backend


preference_schema = {
    'preferences': {'type': 'dict', 'required': True}
}

options_schema = {
    'options': {
        'type': 'string',
        'allowed': ['on', 'off'],
        'default': 'on'
    }
}


def init_app(app):
    endpoint_name = 'preferences'
    service = BaseService(endpoint_name, backend=get_backend())
    PreferencesResource(endpoint_name, app=app, service=service)


class PreferencesResource(Resource):
    datasource = {'source': 'users', 'projection': {'preferences': 1}}
    schema = preference_schema
    resource_methods = ['GET']
    item_methods = ['GET', 'PATCH']
