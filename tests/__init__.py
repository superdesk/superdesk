
import os

os.environ['MONGO_DBNAME'] = 'superdesk_tests'
os.environ['ELASTIC_INDEX'] = 'superdesk_tests'

from superdesk import app, mongo, api

def drop_db():
    with app.test_request_context():
        mongo.cx.drop_database(app.config.get('MONGO_DBNAME'))

def setup(context = None):
    app.config['DEBUG'] = True
    app.config['TESTING'] = True

    if context:
        context.app = app.test_client()
