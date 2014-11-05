
from superdesk.resource import Resource


class PackageResource(Resource):
    '''
    Package schema
    '''
    datasource = {
        'search_backend': 'elastic',
        'default_sort': [('_created', -1)],
    }

    schema = {
        'guid': {
            'type': 'string',
            'unique': True
        },
        'provider': {
            'type': 'string'
        },
        'type': {
            'type': 'string',
            'readonly': True,
            'allowed': ['text', 'audio', 'video', 'picture', 'graphic', 'composite'],
        },
        'associations': {
            'type': 'list',
            'required': True,
            'minlength': 1,
            'schema': {
                'type': 'dict',
                'schema': {
                    'itemRef': {'type': 'string'},
                    'guid': {
                        'type': 'string',
                        'readonly': True
                    },
                    'version': {
                        'type': 'string',
                        'readonly': True
                    },
                    'type': {
                        'type': 'string',
                        'readonly': True
                    },
                    'slugline': {'type': 'string'},
                    'headline': {'type': 'string'},
                }
            }
        },
        'profile': {
            'type': 'string'
        },
        'versioncreated': {
            'type': 'datetime'
        },
        'pubstatus': {
            'type': 'string'
        },
        'copyrightholder': {
            'type': 'string'
        },
        'copyrightnotice': {
            'type': 'string'
        },
        'language': {
            'type': 'string'
        },
        'place': {
            'type': 'list'
        },
        'byline': {
            'type': 'string'
        },
        'headline': {
            'type': 'string'
        },
        'located': {
            'type': 'string'
        },
        'description_text': {
            'type': 'string',
            'nullable': True
        },
        'firstcreated': {
            'type': 'datetime'
        },
        'urgency': {
            'type': 'integer'
        },
        'body_html': {
            'type': 'string'
        },
        'creator': {
            'type': 'dict',
            'schema': {
                'user': Resource.rel('users', True)
            }
        }
    }
