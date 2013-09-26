
import os

if os.environ.get('MONGOLAB_URI'):
    MONGO_URI = os.environ.get('MONGOLAB_URI')
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
