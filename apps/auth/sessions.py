from superdesk.resource import Resource


class SesssionsResource(Resource):
    schema = {
        'user': Resource.rel('users', True)
    }
    datasource = {
        'source': 'auth',
        'default_sort': [('_created', -1)],
        'filter': {'$where': '(ISODate() - this._created) / 3600000 <= 12'}  # last 12h
    }
    resource_methods = ['GET']
    item_methods = []
    embedded_fields = ['user']
