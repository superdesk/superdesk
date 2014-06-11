
import os
import superdesk.tests as tests
from behave import given, when, then  # @UnresolvedImport
from flask import json
from eve.methods.common import parse

from wooper.general import parse_json_input, fail_and_print_body, apply_path,\
    parse_json_response
from wooper.expect import (
    expect_status, expect_status_in,
    expect_json_contains, expect_json_not_contains,
    expect_json_length, expect_headers_contain,
)
from wooper.assertions import (
    assert_in, assert_equal)

external_url = 'http://thumbs.dreamstime.com/z/digital-nature-10485007.jpg'


def test_json(context):
    try:
        response_data = json.loads(context.response.get_data())
    except Exception:
        fail_and_print_body(context.response, 'response is not valid json')

    context_data = parse_json_input(context.text)

    for key in context_data:
        assert_in(key, response_data)
        if context_data[key]:
            assert_equal(response_data[key], context_data[key])


def get_fixture_path(fixture):
    abspath = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(abspath, 'fixtures', fixture)


def get_self_href(resource, context):
    href = resource['_links']['self']['href']
    return href


def get_res(url, context):
    response = context.client.get(url, headers=context.headers)
    expect_status(response, 200)
    return json.loads(response.get_data())


def assert_200(response):
    """Assert we get status code 200."""
    expect_status_in(response, (200, 201))


def assert_404(response):
    """Assert we get status code 404."""
    assert response.status_code == 404, 'Expected 404, got %d' % (response.status_code)


def assert_ok(response):
    """Assert we get ok status within api response."""
    expect_status_in(response, (200, 201))
    expect_json_contains(response, {'_status': 'OK'})


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


@when('we delete it')
def when_we_delete_it(context):
    res = get_json_data(context.response)
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


@when('we patch it')
def step_impl_when_patch_again(context):
    data = get_json_data(context.response)
    href = get_self_href(data, context)
    headers = if_match(context, data.get('_etag'))
    context.response = context.client.patch(href, data=context.text, headers=headers)
    assert_ok(context.response)


@when('we patch first')
def step_impl_when_patch(context):
    href, etag = get_it(context)
    headers = if_match(context, etag)
    context.response = context.client.patch(href, data=context.text, headers=headers)
    assert_ok(context.response)


@when('we get first')
def step_impl_when_get(context):
    href, _etag = get_it(context)
    context.response = context.client.get(href, headers=context.headers)


@when('we upload a binary file to "{dest}"')
def step_impl_when_upload(context, dest):
    with open(get_fixture_path('bike.jpg'), 'rb') as f:
        data = {'media': f}
        headers = [('Content-Type', 'multipart/form-data')]
        headers += context.headers
        context.response = context.client.post(dest, data=data, headers=headers)


@when('we upload a binary file with cropping')
def step_impl_when_upload_with_crop(context):
    with open(get_fixture_path('flower.jpg'), 'rb') as f:
        data = {'media': f, 'CropTop': 0, 'CropLeft': 0, 'CropBottom': 333, 'CropRight': 333}
        headers = [('Content-Type', 'multipart/form-data')]
        headers += context.headers
        context.response = context.client.post('/upload', data=data, headers=headers)


@when('we upload a file from URL')
def step_impl_when_upload_from_url(context):
    data = {'URL': external_url}
    headers = [('Content-Type', 'multipart/form-data')]
    headers += context.headers
    context.response = context.client.post('/upload', data=data, headers=headers)


@when('we upload a file from URL with cropping')
def step_impl_when_upload_from_url_with_crop(context):
    data = {'URL': external_url,
            'CropTop': 0,
            'CropLeft': 0,
            'CropBottom': 333,
            'CropRight': 333}
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
    expect_json_contains(context.response, 'self', path='_links')
    test_json(context)


@then('we get error {code}')
def step_impl_then_get_error(context, code):
    expect_status(context.response, int(code))
    test_json(context)


@then('we get list with {total_count} items')
def step_impl_then_get_list(context, total_count):
    assert_200(context.response)
    expect_json_length(context.response, int(total_count), path='_items')
    if total_count == 0 or not context.text:
        return
    # @TODO: generalize json schema check
    schema = json.loads(context.text)
    response_list = json.loads(context.response.get_data())
    item = response_list['_items'][0]
    for key in schema:
        assert_in(key, item, '%s not in %s' % (key, item))
        if isinstance(schema[key], dict):
            for keykey in schema[key]:
                assert_in(keykey, item[key])
        else:
            assert_equal(schema[key], item[key])


@then('we get no "{field}"')
def step_impl_then_get_nofield(context, field):
    assert_200(context.response)
    expect_json_not_contains(context.response, field)


@then('we get existing resource')
def step_impl_then_get_existing(context):
    assert_200(context.response)
    test_json(context)


@then('we get OK response')
def step_impl_then_get_ok(context):
    assert_ok(context.response)


@then('we get response code {code}')
def step_impl_then_get_code(context, code):
    expect_status(context.response, int(code))


@then('we get updated response')
def step_impl_then_get_updated(context):
    assert_ok(context.response)


@then('we get "{key}" in "{url}"')
def step_impl_then_get_key_in_url(context, key, url):
    res = context.client.get(url, headers=context.headers)
    assert_200(res)
    expect_json_contains(res, key)


@then('we get file metadata')
def step_impl_then_get_file_meta(context):
    expect_json_contains(context.response, 'filemeta')
    meta = apply_path(parse_json_response(context.response), 'filemeta')
    assert isinstance(meta, dict), 'expected dict for file meta'


@then('we get image renditions')
def step_impl_then_get_renditions(context):
    expect_json_contains(context.response, 'renditions')
    renditions = apply_path(parse_json_response(context.response), 'renditions')
    assert isinstance(renditions, dict), 'expected dict for image renditions'
    for rend_name in context.app.config['RENDITIONS']['picture']:
        desc = renditions[rend_name]
        assert isinstance(desc, dict), 'expected dict for rendition description'
        assert 'href' in desc, 'expected href in rendition description'
        assert 'media' in desc, 'expected media identifier in rendition description'


def import_rendition(context, rendition_name=None):
    rv = parse_json_response(context.response)
    headers = [('Content-Type', 'multipart/form-data')]
    headers += context.headers
    context._id = rv['_id']
    context.renditions = rv['renditions']
    data = {'media_archive_guid': rv['_id'], 'href': external_url}
    if rendition_name:
        data['rendition_name'] = rendition_name
    context.response = context.client.post('/archive_media/import_media', data=data, headers=headers)
    assert_200(context.response)


@when('we import rendition from url')
def import_rendition_from_url(context):
    import_rendition(context)


@when('we import thumbnail rendition from url')
def import_thumbnail_rendition_from_url(context):
    import_rendition(context, 'thumbnail')


@when('we get updated media from archive')
def get_updated_media_from_archive(context):
    url = 'archive/%s' % context._id
    step_impl_when_get_url(context, url)
    assert_200(context.response)


@then('baseImage rendition is updated')
def check_base_image_rendition(context):
    check_rendition(context, 'baseImage')


@then('thumbnail rendition is updated')
def check_thumbnail_rendition(context):
    check_rendition(context, 'thumbnail')


def check_rendition(context, rendition_name):
    rv = parse_json_response(context.response)
    print('Got:', rv)
    print('Had:', context.renditions)
    assert rv['renditions'][rendition_name] != context.renditions[rendition_name], rv['renditions']


@then('we get "{key}"')
def step_impl_then_get_key(context, key):
    assert_200(context.response)
    expect_json_contains(context.response, key)


@then('we get action in user activity')
def step_impl_then_get_action(context):
    response = context.client.get('/activity', headers=context.headers)
    expect_json_contains(response, '_items')


@then('we get a file reference')
def step_impl_then_get_file(context):
    assert_200(context.response)
    expect_json_contains(context.response, 'data_uri_url')
    data = get_json_data(context.response)
    url = '/upload/%s' % data['_id']
    headers = [('Accept', 'application/json')]
    headers += context.headers
    response = context.client.get(url, headers=headers)
    assert_200(response)
    assert len(response.get_data()), response
    assert response.mimetype == 'application/json', response.mimetype
    expect_json_contains(response, 'data_uri_url')
    expect_json_contains(response,
                         {'content_type': 'image/jpeg'}, path='media')
    fetched_data = get_json_data(context.response)
    context.fetched_data = fetched_data


@then('the file is not serialized in response')
def step_the_file_is_not_attached_to_response(context):
    assert context.fetched_data['media']['file'] is None, context.fetched_data['media']['file']


@then('the file is serialized in response')
def step_the_file_is_attached_to_response(context):
    assert context.fetched_data['media']['file'] is not None, context.fetched_data['media']['file']


@then('we get cropped data smaller than "{max_size}"')
def step_impl_then_get_cropped_file(context, max_size):
    assert context.fetched_data['media']['length'] < int(max_size), 'was expecting smaller image'


@then('we can fetch a data_uri')
def step_impl_we_fetch_data_uri(context):
    we_can_fetch_an_image(context, context.fetched_data['data_uri_url'])


def we_can_fetch_an_image(context, url):
    headers = [('Accept', 'application/json')]
    headers += context.headers
    response = context.client.get(url, headers=headers)
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
    expect_json_contains(context.response, 'picture_url')


@then('we get facets "{keys}"')
def step_impl_then_get_facets(context, keys):
    assert_200(context.response)
    expect_json_contains(context.response, '_facets')
    data = get_json_data(context.response)
    facets = data['_facets']
    for key in keys.split(','):
        assert_in(key, facets)


@then('the file is stored localy')
def step_impl_then_file(context):
    assert_200(context.response)
    folder = context.app.config['UPLOAD_FOLDER']
    assert os.path.exists(os.path.join(folder, context.filename))


@then('we get etag matching "{url}"')
def step_impl_then_get_etag(context, url):
    if context.app.config['IF_MATCH']:
        assert_200(context.response)
        expect_json_contains(context.response, '_etag')
        etag = get_json_data(context.response).get('_etag')
        response = context.client.get(url, headers=context.headers)
        expect_json_contains(response, {'_etag': etag})


@then('we get not modified response')
def step_impl_then_not_modified(context):
    expect_status(context.response, 304)


@then('we get "{header}" header')
def step_impl_then_get_header(context, header):
    expect_headers_contain(context.response, header)


@then('we get link to "{resource}"')
def then_we_get_link_to_resource(context, resource):
    doc = get_json_data(context.response)
    self_link = doc.get('_links').get('self')
    assert resource in self_link['href'], 'expect link to "%s", got %s' % (resource, self_link)


@then('we get deleted response')
def then_we_get_deleted_response(context):
    assert_200(context.response)
