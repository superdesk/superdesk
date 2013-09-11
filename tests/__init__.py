
import os

os.environ['MONGO_DBNAME'] = 'superdesk_tests'
os.environ['ELASTIC_INDEX'] = 'superdesk_tests'

from superdesk import app, mongo, api

app.config['DEBUG'] = True
app.config['TESTING'] = True

def drop_db():
    with app.test_request_context():
        mongo.cx.drop_database(app.config.get('MONGO_DBNAME'))

def setup(context = None):
    if context:
        context.client = app.test_client()
