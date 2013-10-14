
import os

os.environ['MONGO_DBNAME'] = 'superdesk_tests'
os.environ['ELASTIC_INDEX'] = 'superdesk_tests'

import superdesk

superdesk.app.DEBUG = True
superdesk.app.TESTING = True

from app import application
app = application

def drop_db():
    with application.test_request_context():
        application.data.driver.cx.drop_database(app.config.get('MONGO_DBNAME'))

def setup(context = None):
    if context:
        context.client = application.test_client()
