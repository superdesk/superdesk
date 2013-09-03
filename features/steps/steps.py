
from base64 import b64encode

from behave import *
from flask import json

from superdesk import app
import superdesk.users

JSON_HEADERS = [('Content-Type', 'application/json')]

userdata = {'username': 'foo', 'password': 'bar'}

def create_user(userdata):
    with app.test_request_context():
        superdesk.users.create_user(userdata)
        userdata.pop('_id', None)
        return userdata

def send_auth(userdata, context):
    return context.app.post('/auth', data=json.dumps(userdata), headers=JSON_HEADERS, follow_redirects=True)

@given('a user')
def step_impl(context):
    context.user = create_user(userdata)

@when('we authenticate')
def step_impl(context):
    context.response = send_auth(userdata, context)
    context.token = json.loads(context.response.get_data()).get('token').encode('ascii')

@when('we authenticate with wrong password')
def step_impl(context):
    context.response = send_auth({'username': 'foo', 'password': 'wrong'}, context)

@when('we authenticate with wrong username')
def step_impl(context):
    context.response = send_auth({'username': 'wrong', 'password': 'x'}, context)

@when('we get auth info')
def step_impl(context):
    headers = [('Authorization', b'Basic ' + b64encode(context.token))] if 'token' in context else []
    context.response = context.app.get('/auth', headers=headers, follow_redirects=True)

@then('we get auth token')
def step_impl(context):
    data = json.loads(context.response.get_data())
    assert data.get('token'), data

@then('we get status code "{code}"')
def step_impl(context, code):
    assert context.response.status_code == int(code), context.response.status_code

@then('we get "{text}" in response')
def step_impl(context, text):
    data = context.response.get_data().decode('ascii')
    assert text in data, data
