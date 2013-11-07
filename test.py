
import os
import pymongo
import pyelasticsearch
import settings
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

os.environ['MONGO_DBNAME'] = 'superdesk_tests'
os.environ['ELASTIC_INDEX'] = 'superdesk_tests'

try:
    # drop elastic test index
    es = pyelasticsearch.ElasticSearch(settings.ELASTICSEARCH_URL)
    es.delete_index(os.environ['ELASTIC_INDEX'])
except ElasticHttpNotFoundError:
    pass

import superdesk

superdesk.app.DEBUG = True
superdesk.app.TESTING = True

from app import app as application
app = application

def drop_db():
    with application.test_request_context():
        try:
            application.data.mongo.driver.cx.drop_database(app.config.get('MONGO_DBNAME'))
        except AttributeError:
            pass

def setup(context = None):
    if context:
        context.client = application.test_client()

