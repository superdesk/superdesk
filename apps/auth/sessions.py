from superdesk.resource import Resource


class SessionsResource(Resource):
    schema = {
        'user': Resource.rel('users', True),
        'session_preferences': {'type': 'dict'}
    }
    datasource = {
        'source': 'auth',
        'default_sort': [('_created', -1)]
    }
    resource_methods = ['GET', 'POST']
    item_methods = ['GET', 'DELETE', 'PATCH']
    embedded_fields = ['user']
