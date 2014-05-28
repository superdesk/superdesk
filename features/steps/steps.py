
import os
import superdesk.tests as tests
from behave import given, when, then  # @UnresolvedImport
from flask import json
from eve.methods.common import parse


def test_json(context):
    try:
        response_data = json.loads(context.response.get_data())
    except Exception:
        assert False, 'response is not valid json\nresponse: %s' % (context.response.get_data())

    try:
        context_data = json.loads(context.text)
    except Exception:
        assert False, 'scenario payload is not valid json'

    for key in context_data:
        assert key in response_data, '%s not in %s' % (key, response_data)
        if context_data[key]:
            assert response_data[key] == context_data[key], '"%s" field does not match (%s)' % (key, response_data[key])


def get_fixture_path(fixture):
    abspath = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(abspath, 'fixtures', fixture)


def get_self_href(resource, context):
    href = resource['_links']['self']['href']
    return href


def get_res(url, context):
    response = context.client.get(url, headers=context.headers)
    assert response.status_code == 200, response.get_data()
    return json.loads(response.get_data())


def assert_200(response):
    """Assert we get status code 200."""
    assert response.status_code in (200, 201), 'Expected 20*, got %d' % (response.status_code)


def assert_404(response):
    """Assert we get status code 404."""
    assert response.status_code == 404, 'Expected 404, got %d' % (response.status_code)


def assert_ok(response):
    """Assert we get ok status within api response."""
    assert_200(response)
    data = json.loads(response.get_data())
    assert data['_status'] == 'OK', data


def get_json_data(response):
    return json.loads(response.get_data())


def get_it(context):
    it = context.data[0]
    res = get_res('/%s/%s' % (context.resource, it['_id']), context)
    return get_self_href(res, context), res.get('_etag')


def if_match(context, etag):
    headers = []
    if etag:
        headers = [('If-Match', etag)]
    headers += context.headers
    return headers


def patch_current_user(context, data):
    response = context.client.get('/users/%s' % context.user['_id'], headers=context.headers)
    user = json.loads(response.get_data())
    headers = if_match(context, user.get('_etag'))
    response = context.client.patch('/users/%s' % context.user['_id'], data=data, headers=headers)
    assert_ok(response)
    return response


@given('empty "{resource}"')
def step_impl_given_empty(context, resource):
    with context.app.test_request_context():
        context.app.data.remove(resource)


@given('"{resource}"')
def step_impl_given_(context, resource):
    with context.app.test_request_context():
        context.app.data.remove(resource)
        items = [parse(item, resource) for item in json.loads(context.text)]
        context.app.data.insert(resource, items)
        context.data = items
        context.resource = resource


@given('config')
def step_impl_given_config(context):
    tests.setup(context, json.loads(context.text))
    tests.setup_auth_user(context)


@given('we have "{role_name}" role')
def step_impl_given_role(context, role_name):
    with context.app.test_request_context():
        role = context.app.data.find_one('user_roles', name=role_name)
        data = json.dumps({'role': str(role['_id'])})
    response = patch_current_user(context, data)
    assert_ok(response)


@given('role "{extending_name}" extends "{extended_name}"')
def step_impl_given_role_extends(context, extending_name, extended_name):
    with context.app.test_request_context():
        extended = context.app.data.find_one('user_roles', name=extended_name)
        extending = context.app.data.find_one('user_roles', name=extending_name)
        context.app.data.update('user_roles', extending['_id'], {'extends': extended['_id']})


@when('we post to auth')
def step_impl_when_auth(context):
    data = context.text
    context.response = context.client.post('/auth', data=data, headers=context.headers)


@when('we post to "{url}"')
def step_impl_when_post_url(context, url):
    data = context.text
    context.response = context.client.post(url, data=data, headers=context.headers)


@when('we put to "{url}"')
def step_impl_when_put_url(context, url):
    data = context.text
    href = get_self_href(url)
    context.response = context.client.put(href, data=data, headers=context.headers)
    assert_ok(context.response)


@when('we get "{url}"')
def step_impl_when_get_url(context, url):
    headers = []
    if context.text:
        for line in context.text.split('\n'):
            key, val = line.split(': ')
            headers.append((key, val))
    headers += context.headers
    context.response = context.client.get(url, headers=headers)


@when('we delete "{url}"')
def step_impl_when_delete_url(context, url):
    res = get_res(url, context)
    href = get_self_href(res, context)
    headers = if_match(context, res.get('_etag'))
    context.response = context.client.delete(href, headers=headers)


@when('we patch "{url}"')
def step_impl_when_patch_url(context, url):
    res = get_res(url, context)
    href = get_self_href(res, context)
    headers = if_match(context, res.get('_etag'))
    context.response = context.client.patch(href, data=context.text, headers=headers)
    assert_ok(context.response)


@when('we patch again')
def step_impl_when_patch_again(context):
    data = get_json_data(context.response)
    href = get_self_href(data, context)
    headers = if_match(context, data.get('_etag'))
    context.response = context.client.patch(href, data=context.text, headers=headers)
    assert_ok(context.response)


@when('we patch it')
def step_impl_when_patch(context):
    href, etag = get_it(context)
    headers = if_match(context, etag)
    context.response = context.client.patch(href, data=context.text, headers=headers)
    assert_ok(context.response)


@when('we get it')
def step_impl_when_get(context):
    href, _etag = get_it(context)
    context.response = context.client.get(href, headers=context.headers)


@when('we upload a binary file')
def step_impl_when_upload(context):
    with open(get_fixture_path('flower.jpg'), 'rb') as f:
        data = {'media': f}
        headers = [('Content-Type', 'multipart/form-data')]
        headers += context.headers
        context.response = context.client.post('/upload', data=data, headers=headers)


@when('we upload a binary file with cropping')
def step_impl_when_upload_with_crop(context):
    with open(get_fixture_path('flower.jpg'), 'rb') as f:
        data = {'media': f, 'CropTop': 0, 'CropLeft': 0, 'CropBottom': 333, 'CropRight': 333}
        headers = [('Content-Type', 'multipart/form-data')]
        headers += context.headers
        context.response = context.client.post('/upload', data=data, headers=headers)


@when('we get user profile')
def step_impl_when_get_user(context):
    profile_url = '/%s/%s' % ('users', context.user['_id'])
    context.response = context.client.get(profile_url, headers=context.headers)


@then('we get new resource')
def step_impl_then_get_new(context):
    assert_ok(context.response)
    data = json.loads(context.response.get_data())
    assert data['_links']['self'], data
    test_json(context)


@then('we get error {code}')
def step_impl_then_get_error(context, code):
    assert context.response.status_code == int(code), context.response.status_code
    test_json(context)


@then('we get list with {total_count} items')
def step_impl_then_get_list(context, total_count):
    assert_200(context.response)
    response_list = json.loads(context.response.get_data())
    assert len(response_list['_items']) == int(total_count), 'got %d' % len(response_list['_items'])
    if total_count == 0 or not context.text:
        return

    schema = json.loads(context.text)
    item = response_list['_items'][0]
    for key in schema:
        assert key in item, '%s not in %s' % (key, item)

        if isinstance(schema[key], dict):
            for keykey in schema[key]:
                assert keykey in item[key], '%s not in %s' % (keykey, item[key])
        else:
            assert schema[key] == item[key], '%s not equal to %s' % (schema[key], item[key])


@then('we get no "{field}"')
def step_impl_then_get_nofield(context, field):
    assert_200(context.response)
    response_data = json.loads(context.response.get_data())
    assert field not in response_data, response_data


@then('we get existing resource')
def step_impl_then_get_existing(context):
    assert_200(context.response)
    test_json(context)


@then('we get OK response')
def step_impl_then_get_ok(context):
    assert_ok(context.response)


@then('we get response code {code}')
def step_impl_then_get_code(context, code):
    assert context.response.status_code == int(code), context.response.status_code


@then('we get updated response')
def step_impl_then_get_updated(context):
    assert_ok(context.response)


@then('we get "{key}" in "{url}"')
def step_impl_then_get_key_in_url(context, key, url):
    res = context.client.get(url, headers=context.headers)
    assert_200(res)
    data = get_json_data(res)
    assert data.get(key), '"%s" not in %s' % (key, data)


@then('we get "{key}"')
def step_impl_then_get_key(context, key):
    assert_200(context.response)
    data = get_json_data(context.response)
    assert data.get(key), data


@then('we get action in user activity')
def step_impl_then_get_action(context):
    response = context.client.get('/activity', headers=context.headers)
    data = get_json_data(response)
    assert len(data['_items']), data


@then('we get a file reference')
def step_impl_then_get_file(context):
    assert_200(context.response)
    data = get_json_data(context.response)
    assert data.get('data_uri_url'), 'expecting data_uri_url, got %s' % (data)
    url = '/upload/%s' % data['_id']
    headers = [('Accept', 'application/json')]
    headers += context.headers
    response = context.client.get(url, headers=headers)
    assert_200(response)
    assert len(response.get_data()), response
    assert response.mimetype == 'application/json', response.mimetype
    fetched_data = get_json_data(context.response)
    assert fetched_data['data_uri_url']
    assert fetched_data['media']['content_type'] == 'image/jpeg', fetched_data['media']['content-type']
    context.fetched_data = fetched_data


@then('we get cropped data')
def step_impl_then_get_cropped_file(context):
    assert context.fetched_data['media']['length'] < 15000, 'was expecting smaller image'


@then('we can fetch a data_uri')
def step_impl_we_fetch_data_uri(context):
    headers = [('Accept', 'application/json')]
    headers += context.headers
    response = context.client.get(context.fetched_data['data_uri_url'], headers=headers)
    assert_200(response)
    assert len(response.get_data()), response
    assert response.mimetype == 'image/jpeg', response.mimetype


@then('we can delete that file')
def step_impl_we_delete_file(context):
    url = '/upload/%s' % context.fetched_data['_id']
    headers = [('Accept', 'application/json')]
    headers += context.headers
    response = context.client.delete(url, headers=headers)
    assert_200(response)
    response = context.client.get(url, headers=headers)
    assert_404(response)


@then('we get a picture url')
def step_impl_then_get_picture(context):
    assert_ok(context.response)
    data = get_json_data(context.response)
    assert 'picture_url' in data, data


@then('we get facets "{keys}"')
def step_impl_then_get_facets(context, keys):
    assert_200(context.response)
    data = get_json_data(context.response)
    assert '_facets' in data, data.keys()
    facets = data['_facets']
    for key in keys.split(','):
        assert key in facets, '%s not in [%s]' % (key, ', '.join(facets.keys()))


@then('the file is stored localy')
def step_impl_then_file(context):
    assert_200(context.response)
    folder = context.app.config['UPLOAD_FOLDER']
    assert os.path.exists(os.path.join(folder, context.filename))


@then('we get etag matching "{url}"')
def step_impl_then_get_etag(context, url):
    if context.app.config['IF_MATCH']:
        assert_200(context.response)
        etag = get_json_data(context.response).get('_etag')
        assert etag, 'etag not in %s' % (context.response.data)
        response = context.client.get(url, headers=context.headers)
        data = get_json_data(response)
        assert etag == data.get('_etag'), 'etag %s is not in %s' % (etag, data)


@then('we get not modified response')
def step_impl_then_not_modified(context):
    assert 304 == context.response.status_code, \
        'exptected 304, but it was %d' % context.response.status_code


@then('we get "{header}" header')
def step_impl_then_get_header(context, header):
    assert header in context.response.headers, \
        'expected %s header, but got only %s' % (header, sorted(context.response.headers.keys()))
