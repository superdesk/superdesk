
from behave import *
from flask import json

from tests import app
from superdesk.items import save_item

@given('no items')
def step_impl(context):
    pass

@given('an item')
def step_impl(context):
    with app.test_request_context():
        context.item = save_item({'headline': 'test item'})

@when('we get items')
def step_impl(context):
    context.response = context.client.get('/items', headers=context.headers, follow_redirects=True)

@when('we post new item')
def step_impl(context):
    data = {'headline': 'test'}
    context.response = context.client.post('/items', data=json.dumps(data), headers=context.headers, follow_redirects=True)

@when('we update item')
def step_impl(context):
    context.response = context.client.put('/items/%s' % context.item.get('guid'), data=json.dumps({'headline': 'updated item'}), headers=context.headers, follow_redirects=True)

@then('we get empty list')
def step_impl(context):
    assert context.response.status_code == 200, context.response.status

@then('we get "{prop}" in item')
def step_impl(context, prop):
    item = json.loads(context.response.get_data())
    assert item.get(prop), item

@then('we get updated item')
def step_impl(context):
    item = json.loads(context.response.get_data())
    assert 'updated item' == item.get('headline'), item