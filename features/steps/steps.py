
import os
import superdesk.tests as tests
from behave import given, when, then
from flask import json
from eve.methods.common import parse


def test_json(context):
    response_data = json.loads(context.response.get_data())
    context_data = json.loads(context.text)
    for key in context_data:
        assert key in response_data, key
        if context_data[key]:
            assert response_data[key] == context_data[key], response_data[key]


def get_fixture_path(fixture):
    abspath = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(abspath, 'fixtures', fixture)


def get_self_href(resource, context):
    href = resource['_links']['self']['href']
    return href.replace(context.app.config['SERVER_NAME'], '')


def get_res(url, context):
    response = context.client.get(url, headers=context.headers)
    assert response.status_code == 200, response.get_data()
    return json.loads(response.get_data())


def assert_200(response):
    """Assert we get status code 200."""
    assert response.status_code == 200, '%d\n%s' % (response.status_code, response.get_data().decode('utf-8'))


def assert_ok(response):
    """Assert we get ok status within api response."""
    assert_200(response)
    data = json.loads(response.get_data())
    assert data['status'] == 'OK', data


def get_json_data(response):
    return json.loads(response.get_data())


def get_it(context):
    it = context.data[0]
    res = get_res('/%s/%s' % (context.resource, it['_id']), context)
    return get_self_href(res, context), res['etag']


def if_match(context, etag):
    headers = [('If-Match', etag)]
    headers += context.headers
    return headers


def patch_current_user(context, data):
    response = context.client.get('/users/%s' % context.user['_id'], headers=context.headers)
    user = json.loads(response.get_data())
    headers = if_match(context, user['etag'])
    response = context.client.patch('/users/%s' % context.user['_id'], data=data, headers=headers)
    assert_ok(response)
    return response


@given('empty "{resource}"')
def step_impl(context, resource):
    with context.app.test_request_context():
        context.app.data.remove(resource)


@given('"{resource}"')
def step_impl(context, resource):
    with context.app.test_request_context():
        context.app.data.remove(resource)
        items = [parse(item, resource) for item in json.loads(context.text)]
        context.app.data.insert(resource, items)
        context.data = items
        context.resource = resource


@given('config')
def step_impl(context):
    tests.setup(context, json.loads(context.text))
    tests.setup_auth_user(context)


@given('we have "{role_name}" role')
def step_impl(context, role_name):
    with context.app.test_request_context():
        role = context.app.data.find_one('user_roles', name=role_name)
        data = json.dumps({'user_role': str(role['_id'])})
    response = patch_current_user(context, data)
    assert_ok(response)


@when('we post to auth')
def step_impl(context):
    data = context.text
    context.response = context.client.post('/auth', data=data, headers=context.headers)


@when('we post to "{url}"')
def step_impl(context, url):
    data = context.text
    context.response = context.client.post(url, data=data, headers=context.headers)
    assert_ok(context.response)


@when('we put to "{url}"')
def step_impl(context, url):
    data = context.text
    href = get_self_href(url)
    context.response = context.client.put(href, data=data, headers=context.headers)
    assert_ok(context.response)


@when('we get "{url}"')
def step_impl(context, url):
    context.response = context.client.get(url, headers=context.headers)


@when('we delete "{url}"')
def step_impl(context, url):
    res = get_res(url, context)
    href = get_self_href(res, context)
    headers = [('If-Match', res['etag'])]
    headers += context.headers
    context.response = context.client.delete(href, headers=headers)


@when('we patch "{url}"')
def step_impl(context, url):
    res = get_res(url, context)
    href = get_self_href(res, context)
    headers = [('If-Match', res['etag'])]
    headers += context.headers
    context.response = context.client.patch(href, data=context.text, headers=headers)
    assert_ok(context.response)


@when('we patch it')
def step_impl(context):
    href, etag = get_it(context)
    headers = if_match(context, etag)
    context.response = context.client.patch(href, data=context.text, headers=headers)
    assert_ok(context.response)


@when('we get it')
def step_impl(context):
    href, etag = get_it(context)
    context.response = context.client.get(href, headers=context.headers)


@when('we upload a binary file')
def step_impl(context):
    with open(get_fixture_path('flower.jpg'), 'rb') as f:
        data = {'file': f}
        headers = [('Content-Type', 'multipart/form-data')]
        headers.append(context.headers[1])
        context.response = context.client.post('/upload', data=data, headers=headers)


@then('we get new resource')
def step_impl(context):
    assert_200(context.response)
    data = json.loads(context.response.get_data())
    assert data['status'] == 'OK', data
    assert data['_links']['self'], data
    test_json(context)


@then('we get list with {total_count} items')
def step_impl(context, total_count):
    assert_200(context.response)
    response_list = json.loads(context.response.get_data())
    assert len(response_list['_items']) == int(total_count), response_list
    if total_count == 0 or not context.text:
        return

    schema = json.loads(context.text)
    item = response_list['_items'][0]
    for key in schema:
        assert key in item, '%s not in %s' % (key, item)
        for keykey in schema[key]:
            assert keykey in item[key], '%s not in %s' % (keykey, item[key])


@then('we get no "{field}"')
def step_impl(context, field):
    response_data = json.loads(context.response.get_data())
    assert field not in response_data, response_data


@then('we get existing resource')
def step_impl(context):
    assert_200(context.response)
    test_json(context)


@then('we get OK response')
def step_impl(context):
    assert_200(context.response)


@then('we get response code {code}')
def step_impl(context, code):
    assert context.response.status_code == int(code), context.response.status_code


@then('we get updated response')
def step_impl(context):
    assert_200(context.response)


@then('we get "{key}" in "{url}"')
def step_impl(context, key, url):
    res = context.client.get(url, headers=context.headers)
    assert_200(res)
    data = get_json_data(res)
    assert data.get(key), data


@then('we get "{key}"')
def step_impl(context, key):
    assert_200(context.response)
    data = get_json_data(context.response)
    assert data.get(key), data


@then('we get action in user activity')
def step_impl(context):
    response = context.client.get('/activity', headers=context.headers)
    data = get_json_data(response)
    assert len(data['_items']), data


@then('we get a file reference')
def step_impl(context):
    assert_200(context.response)
    data = get_json_data(context.response)
    assert 'url' in data
    assert 'filename' in data
    context.filename = data['filename']
    response = context.client.get(data['url'], headers=context.headers)
    assert_200(response)
    assert len(response.get_data()), response
    assert response.mimetype == 'image/jpeg', response.mimetype


@then('we get a picture url')
def step_impl(context):
    data = get_json_data(context.response)
    assert 'picture_url' in data, data


@then('we get facets "{keys}"')
def step_impl(context, keys):
    data = get_json_data(context.response)
    assert '_facets' in data, data.keys()
    facets = data['_facets']
    for key in keys.split(','):
        assert key in facets, '%s not in [%s]' % (key, ', '.join(facets.keys()))


@then('the file is stored localy')
def step_impl(context):
    folder = context.app.config['UPLOAD_FOLDER']
    assert os.path.exists(os.path.join(folder, context.filename))
