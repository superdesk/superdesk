from superdesk.models import BaseModel


preference_schema = {
    'preferences': {'type': 'dict', 'required': True}
}


def init_app(app):
    PreferencesModel(app=app)


class PreferencesModel(BaseModel):
    endpoint_name = 'preferences'
    datasource = {'source': 'users', 'projection': {'preferences': 1}}
    schema = preference_schema
    resource_methods = ['GET']
    item_methods = ['GET', 'PATCH']
