
import os

os.environ['MONGOHQ_URL'] = '_test_superdesk'

from superdesk import app, mongo

def before_all(context):
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    context.app = app.test_client()

def after_scenario(context, scenario):
    with app.test_request_context():
        mongo.cx.drop_database(app.config['MONGO_DBNAME'])
