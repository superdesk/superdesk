
import os

# this one must go before any superdesk import
os.environ['MONGOHQ_URL'] = '_test_superdesk'

from superdesk import app, mongo, api

def drop_db():
    with app.test_request_context():
        mongo.cx.drop_database(app.config['MONGO_DBNAME'])

def setup(context = None):
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    drop_db()

    if context:
        context.app = app.test_client()
