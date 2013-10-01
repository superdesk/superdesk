
import os

DEBUG = True

SERVER_NAME = 'localhost:5000'

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

X_DOMAINS = '*'
X_HEADERS = ['Content-Type', 'Authorization']

if os.environ.get('MONGOLAB_URI'):
    MONGO_URI = os.environ.get('MONGOLAB_URI')
    SERVER_NAME = 'superdesk-api.herokuapp.com'

MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'superdesk')

ELASTICSEARCH_URL = os.environ.get('BONSAI_URL', 'http://localhost:9200/')
ELASTICSEARCH_INDEX = os.environ.get('ELASTIC_INDEX', 'superdesk')

INSTALLED_APPS = (
    'superdesk.mongo',
    'superdesk.auth',
    'superdesk.users',
    'superdesk.io',
    'superdesk.items',
    'superdesk.elastic',
)

PUBLIC_METHODS = ['GET']
RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']

LAST_UPDATED = '_updated'
DATE_CREATED = '_created'

DOMAIN = {
    'auth': {
        'schema': {
            'username': {
                'type': 'string'
            },
            'password': {
                'type': 'string'
            }
        },
        'item_methods': []
    },
    'users': {
        'schema': {
            'username': {
                'type': 'string',
                'unique': True,
            },
            'password': {
                'type': 'string',
            },
            'first_name': {
                'type': 'string',
            },
            'last_name': {
                'type': 'string',
            },
            'display_name': {
                'type': 'string',
            },
            'user_info': {
                'type': 'dict'
            }
        },
        'datasource': {
            'projection': {
                'username': 1,
                'first_name': 1,
                'last_name': 1,
                'display_name': 1,
                'user_info': 1,
            }
        }
    },
    'items': {
        'item_title': 'newsItem',
        'resource_methods': ['GET'],
        'last_updated': 'versionCreated',
        'date_created': 'firstCreated',
        'schema': {
            'guid': {
                'type': 'string'

            },
            'headline': {
                'type': 'string'
            },
            'slugline': {
                'type': 'string'
            },
            'firstCreated': {
                'type': 'datetime'
            },
            'versionCreated': {
                'type': 'datetime'
            },
            'itemClass': {
                'type': 'string'
            },
            'provider': {
                'type': 'string'
            },
        },
    }
}
