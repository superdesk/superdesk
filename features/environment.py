
from base64 import b64encode
from flask import json

import tests

from steps.auth import create_user, send_auth

def before_all(context):
    tests.setup(context)

def before_scenario(context, scenario):
    tests.drop_db()
    context.headers = [('Content-Type', 'application/json')]
    if 'auth' in scenario.tags:
        user = {'username': 'tmpuser', 'password': 'tmppassword'}
        create_user(user)
        response = send_auth(user, context)
        token = json.loads(response.get_data()).get('token').encode('ascii')
        context.headers.append(('Authorization', b'Basic ' + b64encode(token)))
