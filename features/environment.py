
from base64 import b64encode
from flask import json

import tests

def before_all(context):
    tests.setup(context)

def before_scenario(context, scenario):
    tests.drop_db()
    context.headers = [('Content-Type', 'application/json')]

    if 'auth' in scenario.tags:
        user = {'username': 'tmpuser', 'password': 'tmppassword'}
        with tests.app.test_request_context():
            tests.app.data.insert('users', [user])
        auth_data = '{"data": %s}' % json.dumps({'username': user['username'], 'password': user['password']})
        auth_response = context.client.post("/auth", data=auth_data, headers=context.headers, follow_redirects=True)
        token = json.loads(auth_response.get_data()).get('data').get('token').encode('ascii')
        context.headers.append(('Authorization', b'basic ' + b64encode(token + b':')))
