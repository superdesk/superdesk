
import os

os.environ['MONGO_DBNAME'] = 'superdesk_tests'
os.environ['ELASTIC_INDEX'] = 'superdesk_tests'

import superdesk

superdesk.app.config['DEBUG'] = True
superdesk.app.config['TESTING'] = True

app = superdesk.app

def drop_db():
    with app.test_request_context():
        app.mongo.cx.drop_database(app.config.get('MONGO_DBNAME'))

def setup(context = None):
    if context:
        context.client = app.test_client()
