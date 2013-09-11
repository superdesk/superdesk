
import os

MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'superdesk')

ELASTIC_INDEX = os.environ.get('ELASTIC_INDEX', 'superdesk')

INSTALLED_APPS = (
    'superdesk.auth',
    'superdesk.items',
    'superdesk.elastic',
)