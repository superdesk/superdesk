
from behave import *
from flask import json

import superdesk.users

@given('no user')
def step_impl(context):
    pass

@given('users')
def step_impl(context):
    superdesk.users.drop_users()
    users = [json.loads(user) for user in context.text.split(',')]
    for userdata in users:
        superdesk.users.create_user(userdata)

@when('we post to "{url}"')
def step_impl(context, url):
    context.response = context.client.post(url, data=context.text, headers=context.headers, follow_redirects=True)

@when('we get "{url}"')
def step_impl(context, url):
    context.response = context.client.get(url, follow_redirects=True)

@then('we get new resource')
def step_impl(context):
    assert context.response.status_code == 201, context.response.status_code
    response_data = json.loads(context.response.get_data())
    context_data = json.loads(context.text)
    for key in context_data:
        assert key in response_data and response_data[key] == context_data[key], key

@then('we get list with {total_count} items')
def step_impl(context, total_count):
    response_list = json.loads(context.response.get_data())
    assert response_list['_list']['total_count'] == int(total_count), response_list
