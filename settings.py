import os

DEBUG = False

MONGO_DBNAME = os.environ.get('MONGOHQ_URL', 'superdesk')

SERVER_NAME = 'localhost:5000'

DATE_CREATED = 'firstCreated'
LAST_UPDATED = 'versionCreated'

DOMAIN = {
    'items': {
        'schema': {
            'guid': {
                'type': 'string',
                'unique': True,
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
    },
}
