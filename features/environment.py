
import os
from base64 import b64encode
from flask import json

os.environ['MONGOHQ_URL'] = '_test_superdesk'

from superdesk import app, mongo
from steps.auth import create_user, send_auth

def drop_db():
    with app.test_request_context():
        mongo.cx.drop_database(app.config['MONGO_DBNAME'])

def before_all(context):
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    context.app = app.test_client()
    drop_db()

def before_scenario(context, scenario):
    context.headers = [('Content-Type', 'application/json')]
    if 'auth' in scenario.tags:
        user = {'username': 'tmpuser', 'password': 'tmppassword'}
        create_user(user)
        response = send_auth(user, context)
        token = json.loads(response.get_data()).get('token').encode('ascii')
        context.headers.append(('Authorization', b'Basic ' + b64encode(token)))

def after_scenario(context, scenario):
    drop_db()
