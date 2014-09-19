from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk import get_backend
from superdesk.utils import ListCursor
import superdesk


preference_schema = {
    'preferences': {'type': 'dict', 'required': True}
}


def init_app(app):
    endpoint_name = 'preferences'
    service = BaseService(endpoint_name, backend=get_backend())
    PreferencesResource(endpoint_name, app=app, service=service)
    endpoint_name = 'available_preferences'
    service = AvailablePreferencesService(endpoint_name, backend=get_backend())
    AvailablePreferencesResource(endpoint_name, app=app, service=service)


class PreferencesResource(Resource):
    datasource = {'source': 'users', 'projection': {'preferences': 1}}
    schema = preference_schema
    resource_methods = ['GET']
    item_methods = ['GET', 'PATCH']


class AvailablePreferencesResource(Resource):
    schema = {}
    resource_methods = ['GET']
    item_methods = []


class AvailablePreferencesService(BaseService):

    def get(self, req, lookup):
        prefs = superdesk.resource_preferences
        return ListCursor(prefs)
