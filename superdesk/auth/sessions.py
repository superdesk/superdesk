from superdesk.base_model import BaseModel


class SesssionsModel(BaseModel):
    endpoint_name = 'sessions'
    schema = {
        'user': BaseModel.rel('users', True)
    }
    datasource = {
        'source': 'auth',
        'default_sort': [('_created', -1)],
        'filter': {'$where': '(ISODate() - this._created) / 3600000 <= 12'}  # last 12h
    }
    resource_methods = ['GET']
    item_methods = []
    embedded_fields = ['user']
