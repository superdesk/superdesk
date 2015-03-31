
from flask import json
from behave import given, when, then
from superdesk import get_resource_service
from superdesk.tests import get_prefixed_url


@given('highlights')
def given_highlights(context):
    with context.app.app_context():
        context.desks = [{'name': 'test'}]
        get_resource_service('desks').post(context.desks)
        context.highlights = [{'name': 'highlight', 'desks': [desk['_id'] for desk in context.desks]}]
        get_resource_service('highlights').post(context.highlights)
        task = {'desk': context.desks[0]['_id']}
        context.items = [{'headline': 'item1', 'task': task}, {'headline': 'item2', 'task': task}]
        get_resource_service('archive').post(context.items)
        for item in context.items:
            marks = [{'highlights': context.highlights[0]['_id'], 'marked_item': item['_id']}]
            get_resource_service('marked_for_highlights').post(marks)


@when('we create highlights package')
def when_we_create_highglights_package(context):
    data = {'highlight': str(context.highlights[0]['_id']), 'type': 'composite'}
    url = get_prefixed_url(context.app, '/archive')
    context.response = context.client.post(url, data=json.dumps(data), headers=context.headers)


@then('we get new package with items')
def then_we_get_new_package_with_items(context):
    assert context.response.status_code == 201, '%d: %s' % (context.response.status_code, context.response.get_data())
    package = json.loads(context.response.get_data())

    groups = package.get('groups')
    assert len(groups) == 2

    refs = groups[1].get('refs')
    assert len(refs) == 2, refs
    assert refs[0]['headline']
    assert refs[1]['headline']
