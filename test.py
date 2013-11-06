
import os

os.environ['MONGO_DBNAME'] = 'superdesk_tests'
os.environ['ELASTIC_INDEX'] = 'superdesk_tests'

import superdesk

superdesk.app.DEBUG = True
superdesk.app.TESTING = True

from app import app as application
app = application

def drop_db():
    with application.test_request_context():
        try:
            application.data.driver.cx.drop_database(app.config.get('MONGO_DBNAME'))
        except AttributeError:
            pass

        try:
            application.data.es.delete_all_indexes()
            application.data.es.refresh()
        except:
            pass

def setup(context = None):
    if context:
        context.client = application.test_client()
