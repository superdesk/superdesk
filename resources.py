items = {
    'schema': {
        'guid': {
            'type': 'string',
            'unique': True,
            'required': True,
        },
        'headline': {
            'type': 'string',
            'required': True,
        },
        'slugline': {
            'type': 'string',
        },
        'creditline': {
            'type': 'string',
        },
        'copyrightHolder': {
            'type': 'string',
        },
        'firstCreated': {
            'type': 'datetime',
        },
        'versionCreated': {
            'type': 'datetime',
        },
        'version': {
            'type': 'integer',
        },
        'itemClass': {
            'type': 'string',
        },
        'contents': {
            'type': 'list',
        },
    },
    'resource_methods': ['GET', 'POST'],
}

users = {
    'schema': {
        'username': {
            'type': 'string',
            'required': True,
            'unique': True,
        },
        'password': {
            'type': 'string',
            'required': True,
        }
    }
}
