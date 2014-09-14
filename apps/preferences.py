from superdesk.models import BaseModel
from superdesk.services import BaseService
from superdesk import get_backend


preference_schema = {
    'preferences': {'type': 'dict', 'required': True}
}


def init_app(app):
    endpoint_name = 'preferences'
    service = BaseService(endpoint_name=endpoint_name, backend=get_backend())
    PreferencesModel(app=app, endpoint_name=endpoint_name, service=service)


class PreferencesModel(BaseModel):
    datasource = {'source': 'users', 'projection': {'preferences': 1}}
    schema = preference_schema
    resource_methods = ['GET']
    item_methods = ['GET', 'PATCH']
