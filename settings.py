
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
)

PUBLIC_METHODS = ['GET']
RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']
