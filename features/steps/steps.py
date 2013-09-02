
from behave import *
from flask import json

from superdesk import app
import superdesk.users

JSON_HEADERS = [('Content-Type', 'application/json')]

def create_user(username, password=None):
    with app.test_request_context():
        user = superdesk.users.create_user(username='foo', password='bar')
        user.pop('_id', None)
        return user

@given('a user')
def step_impl(context):
    context.user = create_user(username='foo', password='bar')

@when('we authenticate')
def step_impl(context):
    context.response = context.app.post('/auth', data=json.dumps(context.user), headers=JSON_HEADERS, follow_redirects=True)

@then('we get auth token')
def step_impl(context):
    data = json.loads(context.response.get_data())
    assert data.get('token'), data
