
import os
import superdesk.tests as tests
from behave import given, when, then  # @UnresolvedImport
from flask import json
from eve.methods.common import parse

from wooper.general import parse_json_input, fail_and_print_body, apply_path,\
    parse_json_response
from wooper.expect import (
    expect_status, expect_status_in,
    expect_json, expect_json_length,
    expect_json_contains, expect_json_not_contains,
    expect_headers_contain,
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
    assert '_links' in resource, 'expted "_links", but got only %s' % (resource)
    return resource['_links']['self']['href']


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
    headers = unique_headers(headers, context.headers)
    return headers


def unique_headers(headers_to_add, old_headers):
    headers = dict(old_headers)
    for item in headers_to_add:
        headers.update({item[0]: item[1]})
    unique_headers = [(k, v) for k, v in headers.items()]
    return unique_headers


def patch_current_user(context, data):
    response = context.client.get('/users/%s' % context.user['_id'], headers=context.headers)
    user = json.loads(response.get_data())
    headers = if_match(context, user.get('_etag'))
    response = context.client.patch('/users/%s' % context.user['_id'], data=data, headers=headers)
    assert_ok(response)
    return response


def set_placeholder(context, name, value):
    old_p = getattr(context, 'placeholders', None)
    if not old_p:
        context.placeholders = dict()
    context.placeholders['#%s#' % name] = value


def apply_placeholders(context, text):
    placeholders = getattr(context, 'placeholders', None)
    if not placeholders:
        return text
    for tag, value in placeholders.items():
        text = text.replace(tag, value)
    return text


@given('empty "{resource}"')
def step_impl_given_empty(context, resource):
    with context.app.test_request_context():
        context.app.data.remove(resource)


@given('"{resource}"')
def step_impl_given_(context, resource):
    with context.app.test_request_context():
        context.app.data.remove(resource)
        items = [parse(item, resource) for item in json.loads(context.text)]
        ev = getattr(context.app, 'on_insert_%s' % resource)
        ev(items)
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
        role = context.app.data.find_one('user_roles', name=role_name, req=None)
        data = json.dumps({'role': str(role['_id'])})
    response = patch_current_user(context, data)
    assert_ok(response)


@given('role "{extending_name}" extends "{extended_name}"')
def step_impl_given_role_extends(context, extending_name, extended_name):
    with context.app.test_request_context():
        extended = context.app.data.find_one('user_roles', name=extended_name, req=None)
        extending = context.app.data.find_one('user_roles', name=extending_name, req=None)
        context.app.data.update('user_roles', extending['_id'], {'extends': extended['_id']})


@when('we post to auth')
def step_impl_when_auth(context):
    data = context.text
    context.response = context.client.post('/auth', data=data, headers=context.headers)


@when('we post to "{url}"')
def step_impl_when_post_url(context, url):
    data = apply_placeholders(context, context.text)
    context.response = context.client.post(url, data=data, headers=context.headers)
    if context.response.status_code in (200, 201):
        item = json.loads(context.response.get_data())
        if item['_status'] == 'OK' and item.get('_id'):
            set_placeholder(context, '%s_ID' % url.upper(), item['_id'])


@when('we put to "{url}"')
def step_impl_when_put_url(context, url):
    data = apply_placeholders(context, context.text)
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
    headers = unique_headers(headers, context.headers)
    context.response = context.client.get(url, headers=headers)


@when('we delete "{url}"')
def step_impl_when_delete_url(context, url):
    res = get_res(url, context)
    href = get_self_href(res, context)
    headers = if_match(context, res.get('_etag'))
    context.response = context.client.delete(href, headers=headers)


@when('we delete latest')
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


@when('we patch latest')
def step_impl_when_patch_again(context):
    data = get_json_data(context.response)
    href = get_self_href(data, context)
    headers = if_match(context, data.get('_etag'))
    context.response = context.client.patch(href, data=context.text, headers=headers)
    assert_ok(context.response)


@when('we patch given')
def step_impl_when_patch(context):
    href, etag = get_it(context)
    headers = if_match(context, etag)
    context.response = context.client.patch(href, data=context.text, headers=headers)
    assert_ok(context.response)


@when('we get given')
def step_impl_when_get(context):
    href, _etag = get_it(context)
    context.response = context.client.get(href, headers=context.headers)


@when('we upload a file "{filename}" to "{dest}"')
def step_impl_when_upload_image(context, filename, dest):
    upload_file(context, dest, filename)


@when('we upload a binary file with cropping')
def step_impl_when_upload_with_crop(context):
    data = {'CropTop': '0', 'CropLeft': '0', 'CropBottom': '333', 'CropRight': '333'}
    upload_file(context, '/upload', 'bike.jpg', crop_data=data)


def upload_file(context, dest, filename, crop_data=None):
    with open(get_fixture_path(filename), 'rb') as f:
        data = {'media': f}
        if crop_data:
            data.update(crop_data)
        headers = [('Content-Type', 'multipart/form-data')]
        headers = unique_headers(headers, context.headers)
        context.response = context.client.post(dest, data=data, headers=headers)
        assert_ok(context.response)


@when('we upload a file from URL')
def step_impl_when_upload_from_url(context):
    data = {'URL': external_url}
    headers = [('Content-Type', 'multipart/form-data')]
    headers = unique_headers(headers, context.headers)
    context.response = context.client.post('/upload', data=data, headers=headers)


@when('we upload a file from URL with cropping')
def step_impl_when_upload_from_url_with_crop(context):
    data = {'URL': external_url,
            'CropTop': '0',
            'CropLeft': '0',
            'CropBottom': '333',
            'CropRight': '333'}
    headers = [('Content-Type', 'multipart/form-data')]
    headers = unique_headers(headers, context.headers)
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
    schema = json.loads(apply_placeholders(context, context.text))
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
    new_url = apply_placeholders(context, url)
    res = context.client.get(new_url, headers=context.headers)
    assert_200(res)
    expect_json_contains(res, key)


@then('we get file metadata')
def step_impl_then_get_file_meta(context):
    assert len(
        apply_path(
            parse_json_response(context.response),
            'filemeta').items()
    ) > 0
    'expected non empty metadata dictionary'


@then('we get "{filename}" metadata')
def step_impl_then_get_file_meta(context, filename):
    if filename == 'image':
        metadata = {
            'YCbCrPositioning': 1,
            'ImageLength': 2448,
            'ExifImageWidth': 2448,
            'MeteringMode': 2,
            'DateTimeDigitized': '2013:08:01 16:19:28',
            'ExposureMode': 0,
            'FlashPixVersion': '0100',
            'ISOSpeedRatings': 80,
            'ImageUniqueID': 'f3533c05daef2debe6257fd99e058eec',
            'DateTimeOriginal': '2013:08:01 16:19:28',
            'WhiteBalance': 0,
            'ExposureProgram': 3,
            'ColorSpace': 1,
            'ExifImageHeight': 3264,
            'Software': 'Google',
            'ResolutionUnit': 2,
            'Make': 'SAMSUNG',
            'MaxApertureValue': [276, 100],
            'ApertureValue': [276, 100],
            'SceneCaptureType': 0,
            'ExposureTime': [1, 2004],
            'DateTime': '2013:08:01 16:19:28',
            'ExifOffset': 216,
            'YResolution': [72, 1],
            'Orientation': 1,
            'ComponentsConfiguration': '0000',
            'ExifVersion': '0220',
            'FocalLength': [37, 10],
            'Flash': 0,
            'Model': 'GT-I9300',
            'XResolution': [72, 1],
            'FNumber': [26, 10],
            'ImageWidth': 3264
        }
    elif filename == 'green.ogg':
        metadata = {
            'producer': 'Xiph.Org libVorbis I 20050304',
            'music_genre': 'New Age',
            'sample_rate': '48000',
            'artist': 'Maxime Abbey',
            'bit_rate': '224000',
            'title': 'Green Hills',
            'mime_type': 'audio/vorbis',
            'format_version': 'Vorbis version 0',
            'comment': '"Green Hills"\\nVersion 2.0 (2007-05-31)\\nCopyright (C) '
                       '2002-2007 Maxime Abbey\\nPlaying Time: '
                       '08:14\\n--------------------------\\nWebsite: '
                       'http://www.arachnosoft.com\\nE-Mail: '
                       'contact@arachnosoft.com\\n--------------------------\\nFreely '
                       'distributed under copyright for personal and non-commercial '
                       'use. Visit http(...)',
            'compression': 'Vorbis',
            'creation_date': '2007-01-01',
            'duration': '0:08:14.728000',
            'endian': 'Little endian',
            'music_composer': 'Maxime Abbey',
            'nb_channel': '2'
        }
    elif filename == 'this_week_nasa.mp4':
        metadata = {
            'mime_type': 'video/mp4',
            'creation_date': '2014-06-13 19:26:17',
            'duration': '0:03:19.733066',
            'width': '480',
            'comment': 'User volume: 100.0%',
            'height': '270',
            'endian': 'Big endian',
            'last_modification': '2014-06-13 19:26:18'
        }
    else:
        raise NotImplementedError("No metadata for file '{}'.".format(filename))

    expect_json(
        context.response,
        metadata,
        path='filemeta'
    )


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
    headers = unique_headers(headers, context.headers)
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


@then('original rendition is updated with link to file having mimetype "{mimetype}"')
def check_original_rendition(context, mimetype):
    rv = parse_json_response(context.response)
    link_to_file = rv['renditions']['original']['href']
    assert link_to_file
    we_can_fetch_a_file(context, link_to_file, mimetype)


@then('thumbnail rendition is updated')
def check_thumbnail_rendition(context):
    check_rendition(context, 'thumbnail')


def check_rendition(context, rendition_name):
    rv = parse_json_response(context.response)
    assert rv['renditions'][rendition_name] != context.renditions[rendition_name], rv['renditions']


@then('we get "{key}"')
def step_impl_then_get_key(context, key):
    assert_200(context.response)
    expect_json_contains(context.response, key)
    item = json.loads(context.response.get_data())
    set_placeholder(context, '%s' % key, item[key])


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
    headers = unique_headers(headers, context.headers)
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
    we_can_fetch_a_file(context, context.fetched_data['data_uri_url'], 'image/jpeg')


def we_can_fetch_a_file(context, url, mimetype):
    headers = [('Accept', 'application/json')]
    headers = unique_headers(headers, context.headers)
    response = context.client.get(url, headers=headers)
    assert_200(response)
    assert len(response.get_data()), response
    assert response.mimetype == mimetype, response.mimetype


@then('we can delete that file')
def step_impl_we_delete_file(context):
    url = '/upload/%s' % context.fetched_data['_id']
    headers = [('Accept', 'application/json')]
    headers = unique_headers(headers, context.headers)
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
