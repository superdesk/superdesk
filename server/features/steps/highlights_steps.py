
from flask import json
from behave import given, when, then
from superdesk import get_resource_service
from superdesk.tests import get_prefixed_url
from superdesk.utc import utcnow
from datetime import timedelta
from features.steps.steps import apply_placeholders


@given('highlights')
def given_highlights(context):
    with context.app.app_context():
        context.desks = {'name': 'test'}
        get_resource_service('desks').post([context.desks])
        context.highlights = {'name': 'highlight', 'desks': [context.desks['_id']],
                              'auto_insert': 'now-12h'}
        get_resource_service('highlights').post([context.highlights])
        task = {'desk': context.desks['_id']}
        context.items = [
            {'headline': 'item1', 'task': task, 'versioncreated': utcnow() - timedelta(minutes=5)},
            {'headline': 'item2', 'task': task, 'versioncreated': utcnow() - timedelta(hours=8)},
            {'headline': 'old', 'task': task, 'versioncreated': utcnow() - timedelta(days=2)},
        ]
        get_resource_service('archive').post(context.items)
        for item in context.items:
            marks = [{'highlights': context.highlights['_id'], 'marked_item': item['_id']}]
            get_resource_service('marked_for_highlights').post(marks)


@when('we create highlights package')
def when_we_create_highglights_package(context):
    data_text = '{"highlight": "%s", "type": "composite", ' \
                '"task": {"user": "#user._id#", "desk": "#desks._id#"}}' \
                % str(context.highlights['_id'])
    data_text = apply_placeholders(context, data_text)
    url = get_prefixed_url(context.app, '/archive')
    context.response = context.client.post(url, data=data_text, headers=context.headers)


@then('we get new package with items')
def then_we_get_new_package_with_items(context):
    assert context.response.status_code == 201, '%d: %s' % (context.response.status_code, context.response.get_data())
    package = json.loads(context.response.get_data())

    groups = package.get('groups')
    assert len(groups) == 2, 'there should be 2 groups'

    refs = groups[1].get('refs')
    assert len(refs) == 2, 'there should be 2 refs %s' % (refs)
    assert refs[0]['headline'] == 'item1', refs[0]
    assert refs[1]['headline'] == 'item2', refs[1]
