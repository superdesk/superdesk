from superdesk.base_view_controller import BaseViewController


def init_app(app):
    SesssionsViewController(app=app)


class SesssionsViewController(BaseViewController):
    endpoint_name = 'sessions'
    schema = {
        'user': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'users',
                'field': '_id',
                'embeddable': True
            }
        }
    }
    datasource = {
        'source': 'auth',
        'default_sort': [('_created', -1)],
        'filter': {'$where': '(ISODate() - this._created) / 3600000 <= 12'}  # last 12h
    }
    resource_methods = ['GET']
    item_methods = []
    embedded_fields = ['user']
