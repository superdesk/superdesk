# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import os
from datetime import datetime, timedelta
from superdesk.io.commands.update_ingest import LAST_ITEM_UPDATE
import superdesk.tests as tests
from behave import given, when, then  # @UnresolvedImport
from flask import json
from eve.methods.common import parse
from superdesk import default_user_preferences, get_resource_service, utc
from superdesk.utc import utcnow
from eve.io.mongo import MongoJSONEncoder
from base64 import b64encode

from wooper.general import fail_and_print_body, apply_path, \
    parse_json_response
from wooper.expect import (
    expect_status, expect_status_in,
    expect_json, expect_json_length,
    expect_json_contains, expect_json_not_contains,
    expect_headers_contain,
)
from wooper.assertions import (
    assert_in, assert_equal)
from urllib.parse import urlparse
from os.path import basename
from superdesk.tests import test_user, get_prefixed_url, set_placeholder
from re import findall
from eve.utils import ParsedRequest
import shutil
from apps.dictionaries.resource import DICTIONARY_FILE

external_url = 'http://thumbs.dreamstime.com/z/digital-nature-10485007.jpg'


def test_json(context):
    try:
        response_data = json.loads(context.response.get_data())
    except Exception:
        fail_and_print_body(context.response, 'response is not valid json')
    context_data = json.loads(apply_placeholders(context, context.text))
    assert_equal(json_match(context_data, response_data), True,
                 msg=str(context_data) + '\n != \n' + str(response_data))
    return response_data


def test_key_is_present(key, context, response):
    """Test if given key is present in response.

    In case the context value is empty - "", {}, [] - it checks if it's non empty in response.

    If it's set in context to false, it will check that it's falsy/empty in response too.

    :param key
    :param context
    :param response
    """
    assert not isinstance(context[key], bool) or not response[key], \
        '"%s" should be empty or false, but it was "%s" in (%s)' % (key, response[key], response)


def json_match(context_data, response_data):
    if isinstance(context_data, dict):
        assert isinstance(response_data, dict), 'response data is not dict, but %s' % type(response_data)
        for key in context_data:
            if key not in response_data:
                print(key, ' not in ', response_data)
                return False
            if context_data[key] == "__any_value__":
                test_key_is_present(key, context_data, response_data)
                continue
            if not json_match(context_data[key], response_data[key]):
                return False
        return True
    elif isinstance(context_data, list):
        for item_context in context_data:
            found = False
            for item_response in response_data:
                if json_match(item_context, item_response):
                    found = True
                    break
            if not found:
                print(item_context, ' not in ', response_data)
                return False
        return True
    elif not isinstance(context_data, dict):
        if context_data != response_data:
            print(context_data, ' != ', response_data)
        return context_data == response_data


def get_fixture_path(fixture):
    abspath = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(abspath, 'fixtures', fixture)


def get_macro_path(macro):
    abspath = os.path.abspath("macros")
    return os.path.join(abspath, macro)


def get_self_href(resource, context):
    assert '_links' in resource, 'expted "_links", but got only %s' % (resource)
    return resource['_links']['self']['href']


def get_res(url, context):
    response = context.client.get(get_prefixed_url(context.app, url), headers=context.headers)
    expect_status(response, 200)
    return json.loads(response.get_data())


def assert_200(response):
    """Assert we get status code 200."""
    expect_status_in(response, (200, 201, 204))


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
    response = context.client.get(get_prefixed_url(context.app, '/users/%s' % context.user['_id']),
                                  headers=context.headers)
    user = json.loads(response.get_data())
    headers = if_match(context, user.get('_etag'))
    response = context.client.patch(get_prefixed_url(context.app, '/users/%s' % context.user['_id']),
                                    data=data, headers=headers)
    assert_ok(response)
    return response


def apply_placeholders(context, text):
    placeholders = getattr(context, 'placeholders', {})
    for placeholder in findall('#([^#"]+)#', text):
        if placeholder not in placeholders:
            try:
                resource_name, field_name = placeholder.lower().split('.', maxsplit=1)
            except:
                continue
            resource = getattr(context, resource_name, None)
            if resource and field_name in resource:
                value = str(resource[field_name])
            else:
                continue
        else:
            value = placeholders[placeholder]
        text = text.replace('#%s#' % placeholder, value)
    return text


def get_resource_name(url):
    parsed_url = urlparse(url)
    return basename(parsed_url.path)


@given('empty "{resource}"')
def step_impl_given_empty(context, resource):
    if not is_user_resource(resource):
        with context.app.test_request_context(context.app.config['URL_PREFIX']):
            get_resource_service(resource).delete_action()


@given('"{resource}"')
def step_impl_given_(context, resource):
    data = apply_placeholders(context, context.text)
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        if not is_user_resource(resource):
            get_resource_service(resource).delete_action()

        items = [parse(item, resource) for item in json.loads(data)]
        if is_user_resource(resource):
            for item in items:
                item.setdefault('needs_activation', False)

        get_resource_service(resource).post(items)
        context.data = items
        context.resource = resource
        setattr(context, resource, items[-1])


@given('the "{resource}"')
def step_impl_given_the(context, resource):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        if not is_user_resource(resource):
            get_resource_service(resource).delete_action()

        orig_items = {}
        items = [parse(item, resource) for item in json.loads(context.text)]
        get_resource_service(resource).post(items)
        context.data = orig_items or items
        context.resource = resource


@given('ingest from "{provider}"')
def step_impl_given_resource_with_provider(context, provider):
    resource = 'ingest'
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        get_resource_service(resource).delete_action()
        items = [parse(item, resource) for item in json.loads(context.text)]
        for item in items:
            item['ingest_provider'] = context.providers[provider]
        get_resource_service(resource).post(items)
        context.data = items
        context.resource = resource


@given('config')
def step_impl_given_config(context):
    tests.setup(context, json.loads(context.text))
    tests.setup_auth_user(context)


@given('we have "{role_name}" role')
def step_impl_given_role(context, role_name):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        role = get_resource_service('roles').find_one(name=role_name, req=None)
        data = MongoJSONEncoder().encode({'role': role.get('_id')})
    response = patch_current_user(context, data)
    assert_ok(response)


@given('we have "{user_type}" as type of user')
def step_impl_given_user_type(context, user_type):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        data = json.dumps({'user_type': user_type})
    response = patch_current_user(context, data)
    assert_ok(response)


@when('we post to auth')
def step_impl_when_auth(context):
    data = context.text
    context.response = context.client.post(get_prefixed_url(context.app, '/auth'), data=data, headers=context.headers)
    if context.response.status_code == 200 or context.response.status_code == 201:
        item = json.loads(context.response.get_data())
        if item.get('_id'):
            set_placeholder(context, 'AUTH_ID', item['_id'])
        context.headers.append(('Authorization', b'basic ' + b64encode(item['token'].encode('ascii') + b':')))
        context.user = item['user']


@given('we create a new macro "{macro_name}"')
def step_create_new_macro(context, macro_name):
    src = get_fixture_path(macro_name)
    dst = get_macro_path(macro_name)
    shutil.copyfile(src, dst)


@when('we fetch from "{provider_name}" ingest "{guid}"')
def step_impl_fetch_from_provider_ingest(context, provider_name, guid):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        fetch_from_provider(context, provider_name, guid)


@when('we fetch from "{provider_name}" ingest "{guid}" using routing_scheme')
def step_impl_fetch_from_provider_ingest_using_routing(context, provider_name, guid):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        _id = apply_placeholders(context, context.text)
        routing_scheme = get_resource_service('routing_schemes').find_one(_id=_id, req=None)
        fetch_from_provider(context, provider_name, guid, routing_scheme)


def fetch_from_provider(context, provider_name, guid, routing_scheme=None):
    ingest_provider_service = get_resource_service('ingest_providers')
    provider = ingest_provider_service.find_one(name=provider_name, req=None)
    provider['routing_scheme'] = routing_scheme
    provider_service = context.provider_services[provider.get('type')]
    provider_service.provider = provider

    if provider.get('type') == 'aap' or provider.get('type') == 'teletype':
        items = provider_service.parse_file(guid, provider)
    else:
        items = provider_service.fetch_ingest(guid)

    for item in items:
        item['versioncreated'] = utcnow()
        item['expiry'] = utcnow() + timedelta(minutes=20)

    failed = context.ingest_items(items, provider, rule_set=provider.get('rule_set'),
                                  routing_scheme=provider.get('routing_scheme'))
    assert len(failed) == 0, failed

    provider = ingest_provider_service.find_one(name=provider_name, req=None)
    ingest_provider_service.system_update(provider['_id'], {LAST_ITEM_UPDATE: utcnow()}, provider)

    for item in items:
        set_placeholder(context, '{}.{}'.format(provider_name, item['guid']), item['_id'])


@when('we post to "{url}"')
def step_impl_when_post_url(context, url):
    post_data(context, url)


def set_user_default(url, data):
    if is_user_resource(url):
        user = json.loads(data)
        user.setdefault('needs_activation', False)
        data = json.dumps(user)


def get_response_etag(response):
    return json.loads(response.get_data())['_etag']


@when('we save etag')
def step_when_we_save_etag(context):
    context.etag = get_response_etag(context.response)


@then('we get same etag')
def step_then_we_get_same_etag(context):
    assert context.etag == get_response_etag(context.response), 'etags not matching'


def store_placeholder(context, url):
    if context.response.status_code in (200, 201):
        item = json.loads(context.response.get_data())
        if item['_status'] == 'OK' and item.get('_id'):
            setattr(context, get_resource_name(url), item)


def post_data(context, url, success=False):
    with context.app.mail.record_messages() as outbox:
        data = apply_placeholders(context, context.text)
        url = apply_placeholders(context, url)
        set_user_default(url, data)
        context.response = context.client.post(get_prefixed_url(context.app, url),
                                               data=data, headers=context.headers)
        if success:
            assert_ok(context.response)

        item = json.loads(context.response.get_data())
        context.outbox = outbox
        store_placeholder(context, url)
        return item


@when('we post to "{url}" with "{tag}" and success')
def step_impl_when_post_url_with_tag(context, url, tag):
    item = post_data(context, url, True)
    if item.get('_id'):
        set_placeholder(context, tag, item.get('_id'))


@given('we have "{url}" with "{tag}" and success')
def step_impl_given_post_url_with_tag(context, url, tag):
    item = post_data(context, url, True)
    if item.get('_id'):
        set_placeholder(context, tag, item.get('_id'))


@when('we post to "{url}" with success')
def step_impl_when_post_url_with_success(context, url):
    post_data(context, url, True)


@when('we put to "{url}"')
def step_impl_when_put_url(context, url):
    with context.app.mail.record_messages() as outbox:
        data = apply_placeholders(context, context.text)
        href = get_self_href(url)
        context.response = context.client.put(get_prefixed_url(context.app, href), data=data, headers=context.headers)
        assert_ok(context.response)
        context.outbox = outbox


@when('we get "{url}"')
def when_we_get_url(context, url):
    url = apply_placeholders(context, url)
    headers = []
    if context.text:
        for line in context.text.split('\n'):
            key, val = line.split(': ')
            headers.append((key, val))
    headers = unique_headers(headers, context.headers)
    url = apply_placeholders(context, url)
    context.response = context.client.get(get_prefixed_url(context.app, url), headers=headers)


@when('we get dictionary "{dictionary_id}"')
def when_we_get_dictionary(context, dictionary_id):
    dictionary_id = apply_placeholders(context, dictionary_id)
    url = '/dictionaries/' + dictionary_id + '?projection={"content": 1}'
    return when_we_get_url(context, url)


@then('we get latest')
def step_impl_we_get_latest(context):
    data = get_json_data(context.response)
    href = get_self_href(data, context)
    headers = if_match(context, data.get('_etag'))
    href = get_prefixed_url(context.app, href)
    context.response = context.client.get(href, headers=headers)
    assert_200(context.response)


@when('we find for "{resource}" the id as "{name}" by "{search_criteria}"')
def when_we_find_for_resource_the_id_as_name_by_search_criteria(context, resource, name, search_criteria):
    url = '/' + resource + '?where=' + search_criteria
    context.response = context.client.get(get_prefixed_url(context.app, url), headers=context.headers)
    if context.response.status_code == 200:
        expect_json_length(context.response, 1, path='_items')
        item = json.loads(context.response.get_data())
        item = item['_items'][0]
        if item.get('_id'):
            set_placeholder(context, name, item['_id'])


@when('we delete "{url}"')
def step_impl_when_delete_url(context, url):
    with context.app.mail.record_messages() as outbox:
        url = apply_placeholders(context, url)
        res = get_res(url, context)
        href = get_self_href(res, context)
        headers = if_match(context, res.get('_etag'))
        href = get_prefixed_url(context.app, href)
        context.response = context.client.delete(href, headers=headers)
        context.outbox = outbox


@when('we delete latest')
def when_we_delete_it(context):
    with context.app.mail.record_messages() as outbox:
        res = get_json_data(context.response)
        href = get_self_href(res, context)
        headers = if_match(context, res.get('_etag'))
        href = get_prefixed_url(context.app, href)
        context.response = context.client.delete(href, headers=headers)
        context.email = outbox


@when('we patch "{url}"')
def step_impl_when_patch_url(context, url):
    with context.app.mail.record_messages() as outbox:
        url = apply_placeholders(context, url)
        res = get_res(url, context)
        href = get_self_href(res, context)
        headers = if_match(context, res.get('_etag'))
        data = apply_placeholders(context, context.text)
        href = get_prefixed_url(context.app, href)
        context.response = context.client.patch(href, data=data, headers=headers)
        context.outbox = outbox


@when('we patch latest')
def step_impl_when_patch_again(context):
    with context.app.mail.record_messages() as outbox:
        data = get_json_data(context.response)
        href = get_prefixed_url(context.app, get_self_href(data, context))
        headers = if_match(context, data.get('_etag'))
        data2 = apply_placeholders(context, context.text)
        context.response = context.client.patch(href, data=data2, headers=headers)
        if context.response.status_code in (200, 201):
            item = json.loads(context.response.get_data())
            if item['_status'] == 'OK' and item.get('_id'):
                setattr(context, get_resource_name(href), item)
        assert_ok(context.response)
        context.outbox = outbox


@when('we patch latest without assert')
def step_impl_when_patch_without_assert(context):
    data = get_json_data(context.response)
    href = get_prefixed_url(context.app, get_self_href(data, context))
    headers = if_match(context, data.get('_etag'))
    data2 = apply_placeholders(context, context.text)
    context.response = context.client.patch(href, data=data2, headers=headers)


@when('we patch routing scheme "{url}"')
def step_impl_when_patch_routing_scheme(context, url):
    with context.app.mail.record_messages() as outbox:
        url = apply_placeholders(context, url)
        res = get_res(url, context)
        href = get_self_href(res, context)
        headers = if_match(context, res.get('_etag'))
        data = json.loads(apply_placeholders(context, context.text))
        res.get('rules', []).append(data)
        context.response = context.client.patch(get_prefixed_url(context.app, href),
                                                data=json.dumps({'rules': res.get('rules', [])}),
                                                headers=headers)
        context.outbox = outbox


@when('we patch given')
def step_impl_when_patch(context):
    with context.app.mail.record_messages() as outbox:
        href, etag = get_it(context)
        headers = if_match(context, etag)
        context.response = context.client.patch(get_prefixed_url(context.app, href), data=context.text, headers=headers)
        assert_ok(context.response)
        context.outbox = outbox


@when('we get given')
def step_impl_when_get(context):
    href, _etag = get_it(context)
    context.response = context.client.get(get_prefixed_url(context.app, href), headers=context.headers)


@when('we restore version {version}')
def step_impl_when_restore_version(context, version):
    data = get_json_data(context.response)
    href = get_self_href(data, context)
    headers = if_match(context, data.get('_etag'))
    text = '{"type": "text", "old_version": %s, "last_version": %s}' % (version, data.get('_current_version'))
    context.response = context.client.put(get_prefixed_url(context.app, href), data=text, headers=headers)
    assert_ok(context.response)


@when('we upload a file "{filename}" to "{dest}"')
def step_impl_when_upload_image(context, filename, dest):
    upload_file(context, dest, filename, 'media')


@when('we upload a binary file with cropping')
def step_impl_when_upload_with_crop(context):
    data = {'CropTop': '0', 'CropLeft': '0', 'CropBottom': '333', 'CropRight': '333'}
    upload_file(context, '/upload', 'bike.jpg', 'media', data)


@when('upload a file "{file_name}" to "{destination}" with "{guid}"')
def step_impl_when_upload_image_with_guid(context, file_name, destination, guid):
    upload_file(context, destination, file_name, 'media', {'guid': guid})


@when('we upload a new dictionary with success')
def when_upload_dictionary(context):
    data = json.loads(apply_placeholders(context, context.text))
    upload_file(context, '/dictionaries', 'test_dict.txt', DICTIONARY_FILE, data)
    assert_ok(context.response)


@when('we upload to an existing dictionary with success')
def when_upload_patch_dictionary(context):
    data = json.loads(apply_placeholders(context, context.text))
    url = apply_placeholders(context, '/dictionaries/#dictionaries._id#')
    etag = apply_placeholders(context, '#dictionaries._etag#')
    upload_file(context, url, 'test_dict2.txt', DICTIONARY_FILE, data, 'patch', [('If-Match', etag)])
    assert_ok(context.response)


def upload_file(context, dest, filename, file_field, extra_data=None, method='post', user_headers=[]):
    with open(get_fixture_path(filename), 'rb') as f:
        data = {file_field: f}
        if extra_data:
            data.update(extra_data)
        headers = [('Content-Type', 'multipart/form-data')]
        headers.extend(user_headers)
        headers = unique_headers(headers, context.headers)
        url = get_prefixed_url(context.app, dest)
        context.response = getattr(context.client, method)(url, data=data, headers=headers)
        assert_ok(context.response)
        store_placeholder(context, url)


@when('we upload a file from URL')
def step_impl_when_upload_from_url(context):
    data = {'URL': external_url}
    headers = [('Content-Type', 'multipart/form-data')]
    headers = unique_headers(headers, context.headers)
    context.response = context.client.post(get_prefixed_url(context.app, '/upload'), data=data, headers=headers)


@when('we upload a file from URL with cropping')
def step_impl_when_upload_from_url_with_crop(context):
    data = {'URL': external_url,
            'CropTop': '0',
            'CropLeft': '0',
            'CropBottom': '333',
            'CropRight': '333'}
    headers = [('Content-Type', 'multipart/form-data')]
    headers = unique_headers(headers, context.headers)
    context.response = context.client.post(get_prefixed_url(context.app, '/upload'), data=data, headers=headers)


@when('we get user profile')
def step_impl_when_get_user(context):
    profile_url = '/%s/%s' % ('users', context.user['_id'])
    context.response = context.client.get(get_prefixed_url(context.app, profile_url), headers=context.headers)


@then('we get new resource')
def step_impl_then_get_new(context):
    assert_ok(context.response)
    expect_json_contains(context.response, 'self', path='_links')
    if context.text is not None:
        return test_json(context)


@then('we get next take as "{new_take}"')
def step_impl_then_get_next_take(context, new_take):
    step_impl_we_get_latest(context)
    data = get_json_data(context.response)
    set_placeholder(context, new_take, data['_id'])
    set_placeholder(context, 'TAKE_PACKAGE', data['takes']['_id'])
    test_json(context)


@then('we get error {code}')
def step_impl_then_get_error(context, code):
    expect_status(context.response, int(code))
    if context.text:
        test_json(context)


@then('we get list with {total_count} items')
def step_impl_then_get_list(context, total_count):
    assert_200(context.response)
    data = get_json_data(context.response)
    int_count = int(total_count.replace('+', ''))

    if '+' in total_count:
        assert int_count <= data['_meta']['total'], '%d items is not enough' % data['_meta']['total']
    else:
        assert int_count == data['_meta']['total'], 'got %d' % (data['_meta']['total'])
    if context.text:
        test_json(context)


@then('we get "{value}" in formatted output')
def step_impl_then_get_formatted_output(context, value):
    assert_200(context.response)
    data = get_json_data(context.response)
    for item in data['_items']:
        if value in item['formatted_item']:
            return
    assert False


@then('we get no "{field}"')
def step_impl_then_get_nofield(context, field):
    assert_200(context.response)
    expect_json_not_contains(context.response, field)


@then('expect json in "{path}"')
def step_impl_then_get_nofield_in_path(context, path):
    assert_200(context.response)
    expect_json(context.response, context.text, path)


@then('we get existing resource')
def step_impl_then_get_existing(context):
    assert_200(context.response)
    test_json(context)


@then('we get OK response')
def step_impl_then_get_ok(context):
    assert_200(context.response)


@then('we get response code {code}')
def step_impl_then_get_code(context, code):
    expect_status(context.response, int(code))


@then('we get updated response')
def step_impl_then_get_updated(context):
    assert_ok(context.response)
    if context.text:
        test_json(context)


@then('we get "{key}" in "{url}"')
def step_impl_then_get_key_in_url(context, key, url):
    url = apply_placeholders(context, url)
    res = context.client.get(get_prefixed_url(context.app, url), headers=context.headers)
    assert_200(res)
    expect_json_contains(res, key)


@then('we get file metadata')
def step_impl_then_get_file_meta(context):
    assert len(
        apply_path(
            parse_json_response(context.response),
            'filemeta'
        ).items()
    ) > 0
    'expected non empty metadata dictionary'


@then('we get "{filename}" metadata')
def step_impl_then_get_given_file_meta(context, filename):
    if filename == 'bike.jpg':
        metadata = {
            'ycbcrpositioning': 1,
            'imagelength': 2448,
            'exifimagewidth': 2448,
            'meteringmode': 2,
            'datetimedigitized': '2013:08:01 16:19:28',
            'exposuremode': 0,
            'flashpixversion': '0100',
            'isospeedratings': 80,
            'length': 469900,
            'imageuniqueid': 'f3533c05daef2debe6257fd99e058eec',
            'datetimeoriginal': '2013:08:01 16:19:28',
            'whitebalance': 0,
            'exposureprogram': 3,
            'colorspace': 1,
            'exifimageheight': 3264,
            'software': 'Google',
            'resolutionunit': 2,
            'make': 'SAMSUNG',
            'maxaperturevalue': [276, 100],
            'aperturevalue': [276, 100],
            'scenecapturetype': 0,
            'exposuretime': [1, 2004],
            'datetime': '2013:08:01 16:19:28',
            'exifoffset': 216,
            'yresolution': [72, 1],
            'orientation': 1,
            'componentsconfiguration': '0000',
            'exifversion': '0220',
            'focallength': [37, 10],
            'flash': 0,
            'model': 'GT-I9300',
            'xresolution': [72, 1],
            'fnumber': [26, 10],
            'imagewidth': 3264
        }
    elif filename == 'green.ogg':
        metadata = {
            'producer': 'Lavf54.59.103',
            'music_genre': 'New Age',
            'sample_rate': '44100',
            'artist': 'Maxime Abbey',
            'length': 368058,
            'bit_rate': '160000',
            'title': 'Green Hills',
            'mime_type': 'audio/vorbis',
            'format_version': 'Vorbis version 0',
            'compression': 'Vorbis',
            'duration': '0:00:20.088163',
            'endian': 'Little endian',
            'nb_channel': '2'
        }
    elif filename == 'this_week_nasa.mp4':
        metadata = {
            'mime_type': 'video/mp4',
            'creation_date': '1904-01-01T00:00:00+00:00',
            'duration': '0:00:10.224000',
            'width': '480',
            'length': 877869,
            'comment': 'User volume: 100.0%',
            'height': '270',
            'endian': 'Big endian',
            'last_modification': '1904-01-01T00:00:00+00:00'
        }
    else:
        raise NotImplementedError("No metadata for file '{}'.".format(filename))

    expect_json(
        context.response,
        metadata,
        path='filemeta'
    )


@then('we get "{type}" renditions')
def step_impl_then_get_renditions(context, type):
    expect_json_contains(context.response, 'renditions')
    renditions = apply_path(parse_json_response(context.response), 'renditions')
    assert isinstance(renditions, dict), 'expected dict for image renditions'
    for rend_name in context.app.config['RENDITIONS'][type]:
        desc = renditions[rend_name]
        assert isinstance(desc, dict), 'expected dict for rendition description'
        assert 'href' in desc, 'expected href in rendition description'
        assert 'media' in desc, 'expected media identifier in rendition description'
        we_can_fetch_a_file(context, desc['href'], 'image/jpeg')


@then('item "{item_id}" is unlocked')
def then_item_is_unlocked(context, item_id):
    assert_200(context.response)
    data = json.loads(context.response.get_data())
    assert data.get('lock_user', None) is None, 'item is locked by user #{0}'.format(data.get('lock_user'))


@then('item "{item_id}" is locked')
def then_item_is_locked(context, item_id):
    assert_200(context.response)
    resp = parse_json_response(context.response)
    assert resp['lock_user'] is not None


@then('item "{item_id}" is assigned')
def then_item_is_assigned(context, item_id):
    resp = parse_json_response(context.response)
    assert resp['task'].get('user', None) is not None, 'item is not assigned'


@then('we get rendition "{name}" with mimetype "{mimetype}"')
def step_impl_then_get_rendition_with_mimetype(context, name, mimetype):
    expect_json_contains(context.response, 'renditions')
    renditions = apply_path(parse_json_response(context.response), 'renditions')
    assert isinstance(renditions, dict), 'expected dict for image renditions'
    desc = renditions[name]
    assert isinstance(desc, dict), 'expected dict for rendition description'
    assert 'href' in desc, 'expected href in rendition description'
    we_can_fetch_a_file(context, desc['href'], mimetype)


@when('we get updated media from archive')
def get_updated_media_from_archive(context):
    url = 'archive/%s' % context._id
    when_we_get_url(context, url)
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
    response = context.client.get(get_prefixed_url(context.app, '/activity'), headers=context.headers)
    expect_json_contains(response, '_items')


@then('we get a file reference')
def step_impl_then_get_file(context):
    assert_200(context.response)
    expect_json_contains(context.response, 'renditions')
    data = get_json_data(context.response)
    url = '/upload/%s' % data['_id']
    headers = [('Accept', 'application/json')]
    headers = unique_headers(headers, context.headers)
    response = context.client.get(get_prefixed_url(context.app, url), headers=headers)
    assert_200(response)
    assert len(response.get_data()), response
    assert response.mimetype == 'application/json', response.mimetype
    expect_json_contains(response, 'renditions')
    expect_json_contains(response, {'mime_type': 'image/jpeg'})
    fetched_data = get_json_data(context.response)
    context.fetched_data = fetched_data


@then('we get cropped data smaller than "{max_size}"')
def step_impl_then_get_cropped_file(context, max_size):
    assert int(context.fetched_data['filemeta']['length']) < int(max_size), 'was expecting smaller image'


@then('we can fetch a data_uri')
def step_impl_we_fetch_data_uri(context):
    we_can_fetch_a_file(context, context.fetched_data['renditions']['original']['href'], 'image/jpeg')


def we_can_fetch_a_file(context, url, mimetype):
    headers = [('Accept', 'application/json')]
    headers = unique_headers(headers, context.headers)
    response = context.client.get(get_prefixed_url(context.app, url), headers=headers)
    assert_200(response)
    assert len(response.get_data()), response
    assert response.mimetype == mimetype, response.mimetype


@then('we can delete that file')
def step_impl_we_delete_file(context):
    url = '/upload/%s' % context.fetched_data['_id']
    context.headers.append(('Accept', 'application/json'))
    headers = if_match(context, context.fetched_data.get('_etag'))
    response = context.client.delete(get_prefixed_url(context.app, url), headers=headers)
    assert_200(response)
    response = context.client.get(get_prefixed_url(context.app, url), headers=headers)
    assert_404(response)


@then('we get a picture url')
def step_impl_then_get_picture(context):
    assert_ok(context.response)
    expect_json_contains(context.response, 'picture_url')


@then('we get aggregations "{keys}"')
def step_impl_then_get_aggs(context, keys):
    assert_200(context.response)
    expect_json_contains(context.response, '_aggregations')
    data = get_json_data(context.response)
    aggs = data['_aggregations']
    for key in keys.split(','):
        assert_in(key, aggs)


@then('the file is stored localy')
def step_impl_then_file(context):
    assert_200(context.response)
    folder = context.app.config['UPLOAD_FOLDER']
    assert os.path.exists(os.path.join(folder, context.filename))


@then('we get version {version}')
def step_impl_then_get_version(context, version):
    assert_200(context.response)
    expect_json_contains(context.response, {'_current_version': int(version)})


@then('the field "{field}" value is "{value}"')
def step_impl_then_get_field_value(context, field, value):
    assert_200(context.response)
    expect_json_contains(context.response, {field: value})


@then('we get etag matching "{url}"')
def step_impl_then_get_etag(context, url):
    if context.app.config['IF_MATCH']:
        assert_200(context.response)
        expect_json_contains(context.response, '_etag')
        etag = get_json_data(context.response).get('_etag')
        response = context.client.get(get_prefixed_url(context.app, url), headers=context.headers)
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


@when('we post to reset_password we get email with token')
def we_post_to_reset_password(context):
    data = {'email': 'foo@bar.org'}
    headers = [('Content-Type', 'multipart/form-data')]
    headers = unique_headers(headers, context.headers)
    with context.app.mail.record_messages() as outbox:
        context.response = context.client.post(get_prefixed_url(context.app, '/reset_user_password'),
                                               data=data, headers=headers)
        expect_status_in(context.response, (200, 201))
        assert len(outbox) == 1
        assert outbox[0].subject == "Reset password"
        email_text = outbox[0].body
        assert "24" in email_text
        words = email_text.split()
        url = urlparse(words[words.index("link") + 1])
        token = url.fragment.split('token=')[-1]
        assert token
        context.token = token


@then('we can check if token is valid')
def we_can_check_token_is_valid(context):
    data = {'token': context.token}
    headers = [('Content-Type', 'multipart/form-data')]
    headers = unique_headers(headers, context.headers)
    context.response = context.client.post(get_prefixed_url(context.app, '/reset_user_password'),
                                           data=data, headers=headers)
    expect_status_in(context.response, (200, 201))


@then('we update token to be expired')
def we_update_token_to_expired(context):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        expiry = utc.utcnow() - timedelta(days=2)
        reset_request = get_resource_service('reset_user_password').find_one(req=None, token=context.token)
        reset_request['expire_time'] = expiry
        id = reset_request.pop('_id')
        get_resource_service('reset_user_password').patch(id, reset_request)


@then('token is invalid')
def check_token_invalid(context):
    data = {'token': context.token}
    headers = [('Content-Type', 'multipart/form-data')]
    headers = unique_headers(headers, context.headers)
    context.response = context.client.post(get_prefixed_url(context.app, '/reset_user_password'),
                                           data=data, headers=headers)
    expect_status_in(context.response, (403, 401))


@when('we post to reset_password we do not get email with token')
def we_post_to_reset_password_it_fails(context):
    data = {'email': 'foo@bar.org'}
    headers = [('Content-Type', 'multipart/form-data')]
    headers = unique_headers(headers, context.headers)
    with context.app.mail.record_messages() as outbox:
        context.response = context.client.post(get_prefixed_url(context.app, '/reset_user_password'),
                                               data=data, headers=headers)
        expect_status_in(context.response, (200, 201))
        assert len(outbox) == 0


def start_reset_password_for_user(context):
    data = {'token': context.token, 'password': 'test_pass'}
    headers = [('Content-Type', 'multipart/form-data')]
    headers = unique_headers(headers, context.headers)
    context.response = context.client.post(get_prefixed_url(context.app, '/reset_user_password'),
                                           data=data, headers=headers)


@then('we fail to reset password for user')
def we_fail_to_reset_password_for_user(context):
    start_reset_password_for_user(context)
    step_impl_then_get_error(context, 403)


@then('we reset password for user')
def we_reset_password_for_user(context):
    start_reset_password_for_user(context)
    expect_status_in(context.response, (200, 201))

    auth_data = {'username': 'foo', 'password': 'test_pass'}
    headers = [('Content-Type', 'multipart/form-data')]
    headers = unique_headers(headers, context.headers)
    context.response = context.client.post(get_prefixed_url(context.app, '/auth'), data=auth_data, headers=headers)
    expect_status_in(context.response, (200, 201))


@when('we switch user')
def when_we_switch_user(context):
    user = {'username': 'test-user-2', 'password': 'pwd', 'is_active': True,
            'needs_activation': False, 'sign_off': 'foo'}
    tests.setup_auth_user(context, user)
    set_placeholder(context, 'USERS_ID', str(context.user['_id']))


@when('we setup test user')
def when_we_setup_test_user(context):
    tests.setup_auth_user(context, test_user)


@when('we get my "{url}"')
def when_we_get_my_url(context, url):
    user_id = str(context.user.get('_id'))
    my_url = '{0}?where={1}'.format(url, json.dumps({'user': user_id}))
    return when_we_get_url(context, my_url)


@when('we get user "{resource}"')
def when_we_get_user_resource(context, resource):
    url = '/users/{0}/{1}'.format(str(context.user.get('_id')), resource)
    return when_we_get_url(context, url)


@then('we get embedded items')
def we_get_embedded_items(context):
    response_data = json.loads(context.response.get_data())
    href = get_self_href(response_data, context)
    url = href + '/?embedded={"items": 1}'
    context.response = context.client.get(get_prefixed_url(context.app, url), headers=context.headers)
    assert_200(context.response)
    context.response_data = json.loads(context.response.get_data())
    assert len(context.response_data['items']['view_items']) == 2


@when('we reset notifications')
def step_when_we_reset_notifications(context):
    context.app.notification_client.reset()


@then('we get notifications')
def then_we_get_notifications(context):
    notifications = context.app.notification_client.messages
    notifications_data = [json.loads(notification) for notification in notifications]
    context_data = json.loads(apply_placeholders(context, context.text))
    assert_equal(json_match(context_data, notifications_data), True,
                 msg=str(context_data) + '\n != \n' + str(notifications_data))


@then('we get default preferences')
def get_default_prefs(context):
    response_data = json.loads(context.response.get_data())
    assert_equal(response_data['user_preferences'], default_user_preferences)


@when('we spike "{item_id}"')
def step_impl_when_spike_url(context, item_id):
    item_id = apply_placeholders(context, item_id)
    res = get_res('/archive/' + item_id, context)
    headers = if_match(context, res.get('_etag'))

    context.response = context.client.patch(get_prefixed_url(context.app, '/archive/spike/' + item_id),
                                            data='{"state": "spiked"}', headers=headers)


@when('we spike fetched item')
def step_impl_when_spike_fetched_item(context):
    data = json.loads(apply_placeholders(context, context.text))
    item_id = data["_id"]
    res = get_res('/archive/' + item_id, context)
    headers = if_match(context, res.get('_etag'))

    context.response = context.client.patch(get_prefixed_url(context.app, '/archive/spike/' + item_id),
                                            data='{"state": "spiked"}', headers=headers)


@when('we unspike "{item_id}"')
def step_impl_when_unspike_url(context, item_id):
    res = get_res('/archive/' + item_id, context)
    headers = if_match(context, res.get('_etag'))
    context.response = context.client.patch(get_prefixed_url(context.app, '/archive/unspike/' + item_id),
                                            data='{}', headers=headers)


@then('we get spiked content "{item_id}"')
def get_spiked_content(context, item_id):
    item_id = apply_placeholders(context, item_id)
    url = 'archive/{0}'.format(item_id)
    when_we_get_url(context, url)
    assert_200(context.response)
    response_data = json.loads(context.response.get_data())
    assert_equal(response_data['state'], 'spiked')
    assert_equal(response_data['operation'], 'spike')


@then('we get unspiked content "{id}"')
def get_unspiked_content(context, id):
    url = 'archive/{0}'.format(id)
    when_we_get_url(context, url)
    assert_200(context.response)
    response_data = json.loads(context.response.get_data())
    assert_equal(response_data['state'], 'draft')
    assert_equal(response_data['operation'], 'unspike')
    # Tolga Akin (05/11/14)
    # Expiry value doesn't get set to None properly in Elastic.
    # Discussed with Petr so we'll look into this later
    # assert_equal(response_data['expiry'], None)


@then('we get global spike expiry')
def get_global_spike_expiry(context):
    get_desk_spike_expiry(context, context.app.config['SPIKE_EXPIRY_MINUTES'])


@then('we get global content expiry')
def get_global_content_expiry(context):
    get_desk_spike_expiry(context, context.app.config['CONTENT_EXPIRY_MINUTES'])


@then('we get content expiry {minutes}')
def get_content_expiry(context, minutes):
    get_desk_spike_expiry(context, int(minutes))


@then('we get desk spike expiry after "{test_minutes}"')
def get_desk_spike_expiry(context, test_minutes):
    response_data = json.loads(context.response.get_data())
    assert response_data['expiry']
    response_expiry = datetime.strptime(response_data['expiry'], "%Y-%m-%dT%H:%M:%S%z")
    expiry = utc.utcnow() + timedelta(minutes=int(test_minutes))
    assert response_expiry <= expiry


@when('we mention user in comment for "{url}"')
def we_mention_user_in_comment(context, url):
    with context.app.mail.record_messages() as outbox:
        step_impl_when_post_url(context, url)
        assert len(outbox) == 1
        assert_equal(outbox[0].subject, "You were mentioned in a comment by test_user")
        email_text = outbox[0].body
        assert email_text


@when('we change user status to "{status}" using "{url}"')
def we_change_user_status(context, status, url):
    with context.app.mail.record_messages() as outbox:
        step_impl_when_patch_url(context, url)
        assert len(outbox) == 1
        assert_equal(outbox[0].subject, "Your Superdesk account is " + status)
        assert outbox[0].body


@when('we get the default incoming stage')
def we_get_default_incoming_stage(context):
    data = json.loads(context.response.get_data())
    incoming_stage = data['_items'][0]['incoming_stage']
    assert incoming_stage
    url = 'stages/{0}'.format(incoming_stage)
    when_we_get_url(context, url)
    assert_200(context.response)
    data = json.loads(context.response.get_data())
    assert data['default_incoming'] is True
    assert data['name'] == 'New'


@then('we get stage filled in to default_incoming')
def we_get_stage_filled_in(context):
    data = json.loads(context.response.get_data())
    assert data['task']['stage']


@given('we have sessions "{url}"')
def we_have_sessions_get_id(context, url):
    when_we_get_url(context, url)
    item = json.loads(context.response.get_data())
    context.session_id = item['_items'][0]['_id']
    context.data = item
    set_placeholder(context, 'SESSION_ID', item['_items'][0]['_id'])
    setattr(context, 'users', item['_items'][0]['user'])


@then('we get session by id')
def we_get_session_by_id(context):
    url = 'sessions/' + context.session_id
    when_we_get_url(context, url)
    item = json.loads(context.response.get_data())
    returned_id = item["_id"]
    assert context.session_id == returned_id


@then('we delete session by id')
def we_delete_session_by_id(context):
    url = 'sessions/' + context.session_id
    step_impl_when_delete_url(context, url)
    assert_200(context.response)


@when('we create a new user')
def step_create_a_user(context):
    data = apply_placeholders(context, context.text)
    with context.app.mail.record_messages() as outbox:
        context.response = context.client.post(get_prefixed_url(context.app, '/users'),
                                               data=data, headers=context.headers)
        expect_status_in(context.response, (200, 201))
        assert len(outbox) == 1
        context.email = outbox[0]


@then('we get activation email')
def step_get_activation_email(context):
    assert context.email.subject == 'Superdesk account created'
    email_text = context.email.body
    words = email_text.split()
    url = urlparse(words[words.index("to") + 1])
    token = url.fragment.split('token=')[-1]
    assert token


@then('we set elastic limit')
def step_set_limit(context):
    context.app.settings['MAX_SEARCH_DEPTH'] = 1


@then('we get emails')
def step_we_get_email(context):
    data = json.loads(context.text)
    for email in data:
        assert check_if_email_sent(context, email['body'])


@then('we get no email')
def step_we_get_no_email(context):
    assert len(context.outbox) == 0


def check_if_email_sent(context, body):
    if context.outbox:
        for email in context.outbox:
            if body in email.body:
                return True
        return False


@then('we get activity')
def then_we_get_activity(context):
    url = apply_placeholders(context, '/activity?where={"name": "notify"}')
    context.response = context.client.get(get_prefixed_url(context.app, url), headers=context.headers)
    if context.response.status_code == 200:
        expect_json_length(context.response, 1, path='_items')
        item = json.loads(context.response.get_data())
        item = item['_items'][0]
        if item.get('_id'):
            setattr(context, 'activity', item)
            set_placeholder(context, 'USERS_ID', item['user'])


def login_as(context, username, password, user_type):
    user = {'username': username, 'password': password, 'is_active': True,
            'is_enabled': True, 'needs_activation': False, user_type: user_type}

    if context.text:
        user.update(json.loads(context.text))

    tests.setup_auth_user(context, user)


@given('we login as user "{username}" with password "{password}" and user type "{user_type}"')
def given_we_login_as_user(context, username, password, user_type):
    login_as(context, username, password, user_type)


@when('we login as user "{username}" with password "{password}" and user type "{user_type}"')
def when_we_login_as_user(context, username, password, user_type):
    login_as(context, username, password, user_type)


def is_user_resource(resource):
    return resource in ('users', '/users')


@then('we get {no_of_stages} invisible stages')
def when_we_get_invisible_stages(context, no_of_stages):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        stages = get_resource_service('stages').get_stages_by_visibility(is_visible=False)
        assert len(stages) == int(no_of_stages)


@then('we get {no_of_stages} visible stages')
def when_we_get_visible_stages(context, no_of_stages):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        stages = get_resource_service('stages').get_stages_by_visibility(is_visible=True)
        assert len(stages) == int(no_of_stages)


@then('we get {no_of_stages} invisible stages for user')
def when_we_get_invisible_stages_for_user(context, no_of_stages):
    data = json.loads(apply_placeholders(context, context.text))
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        stages = get_resource_service('users').get_invisible_stages(data['user'])
        assert len(stages) == int(no_of_stages)


@then('we get "{field_name}" populated')
def then_field_is_populated(context, field_name):
    resp = parse_json_response(context.response)
    assert resp[field_name].get('user', None) is not None, 'item is not populated'


@then('we get "{field_name}" not populated')
def then_field_is_not_populated(context, field_name):
    resp = parse_json_response(context.response)
    assert resp[field_name] is None, 'item is not populated'


@then('we get "{field_name}" not populated in results')
def then_field_is_not_populated(context, field_name):
    resps = parse_json_response(context.response)
    for resp in resps['_items']:
        assert resp[field_name] is None, 'item is not populated'


@when('we delete publish filter "{name}"')
def step_delete_publish_filter(context, name):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        filter = get_resource_service('publish_filters').find_one(req=None, name=name)
        url = '/publish_filters/{}'.format(filter['_id'])
        headers = if_match(context, filter.get('_etag'))
        context.response = context.client.delete(get_prefixed_url(context.app, url), headers=headers)


@when('we rewrite "{item_id}"')
def step_impl_when_rewrite(context, item_id):
    context_data = {}
    _id = apply_placeholders(context, item_id)
    if context.text:
        context_data.update(json.loads(apply_placeholders(context, context.text)))
    data = json.dumps(context_data)
    context.response = context.client.post(
        get_prefixed_url(context.app, '/archive/{}/rewrite'.format(_id)),
        data=data, headers=context.headers)
    if context.response.status_code == 400:
        return

    resp = parse_json_response(context.response)
    set_placeholder(context, 'REWRITE_OF', _id)
    set_placeholder(context, 'REWRITE_ID', resp['_id']['_id'])


@when('we publish "{item_id}" with "{pub_type}" type and "{state}" state')
def step_impl_when_publish_url(context, item_id, pub_type, state):
    item_id = apply_placeholders(context, item_id)
    res = get_res('/archive/' + item_id, context)
    headers = if_match(context, res.get('_etag'))
    context_data = {"state": state}
    if context.text:
        context_data.update(json.loads(context.text))
    data = json.dumps(context_data)
    context.response = context.client.patch(get_prefixed_url(context.app, '/archive/{}/{}'.format(pub_type, item_id)),
                                            data=data, headers=headers)
    resp = parse_json_response(context.response)
    linked_packages = resp.get('linked_in_packages', [])
    if linked_packages:
        take_package = linked_packages[0].get('package', '')
        set_placeholder(context, 'archive.{}.take_package'.format(item_id), take_package)


@then('the ingest item is routed based on routing scheme and rule "{rule_name}"')
def then_ingest_item_is_routed_based_on_routing_scheme(context, rule_name):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        validate_routed_item(context, rule_name, True)


@then('the ingest item is routed and transformed based on routing scheme and rule "{rule_name}"')
def then_ingest_item_is_routed_transformed_based_on_routing_scheme(context, rule_name):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        validate_routed_item(context, rule_name, True, True)


@then('the ingest item is not routed based on routing scheme and rule "{rule_name}"')
def then_ingest_item_is_not_routed_based_on_routing_scheme(context, rule_name):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        validate_routed_item(context, rule_name, False)


def validate_routed_item(context, rule_name, is_routed, is_transformed=False):
    data = json.loads(apply_placeholders(context, context.text))

    def validate_rule(action, state):
        for destination in rule.get('actions', {}).get(action, []):
            query = {
                'and': [
                    {'term': {'ingest_id': str(data['ingest'])}},
                    {'term': {'task.desk': str(destination['desk'])}},
                    {'term': {'task.stage': str(destination['stage'])}},
                    {'term': {'state': state}}
                ]
            }
            item = get_archive_items(query) + get_published_items(query)

            if is_routed:
                assert len(item) > 0, 'No routed items found for criteria: ' + str(query)
                assert item[0]['ingest_id'] == data['ingest']
                assert item[0]['task']['desk'] == str(destination['desk'])
                assert item[0]['task']['stage'] == str(destination['stage'])
                assert item[0]['state'] == state

                if is_transformed:
                    assert item[0]['abstract'] == 'Abstract has been updated'

                assert_items_in_package(item[0], state, str(destination['desk']), str(destination['stage']))
            else:
                assert len(item) == 0

    scheme = get_resource_service('routing_schemes').find_one(_id=data['routing_scheme'], req=None)
    rule = next((rule for rule in scheme['rules'] if rule['name'].lower() == rule_name.lower()), {})
    validate_rule('fetch', 'routed')
    validate_rule('publish', 'published')


@when('we schedule the routing scheme "{scheme_id}"')
def when_we_schedule_the_routing_scheme(context, scheme_id):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        scheme_id = apply_placeholders(context, scheme_id)
        url = apply_placeholders(context, 'routing_schemes/%s' % scheme_id)
        res = get_res(url, context)
        href = get_self_href(res, context)
        headers = if_match(context, res.get('_etag'))
        rule = res.get('rules')[0]
        day_of_week = get_resource_service('routing_schemes').day_of_week
        rule['schedule'] = {
            'day_of_week': [day_of_week[(datetime.now() + timedelta(days=1)).weekday()],
                            day_of_week[(datetime.now() + timedelta(days=2)).weekday()]],
            'hour_of_day_from': '1600',
            'hour_of_day_to': '2000'
        }
        rule = res.get('rules')[1]
        rule['schedule'] = {
            'day_of_week': [day_of_week[datetime.now().weekday()]]
        }

        context.response = context.client.patch(get_prefixed_url(context.app, href),
                                                data=json.dumps({'rules': res.get('rules', [])}),
                                                headers=headers)
        assert_200(context.response)


def get_archive_items(query):
    req = ParsedRequest()
    req.max_results = 100
    req.args = {'filter': json.dumps(query)}
    return list(get_resource_service('archive').get(lookup=None, req=req))


def get_published_items(query):
    req = ParsedRequest()
    req.max_results = 100
    req.args = {'filter': json.dumps(query)}
    return list(get_resource_service('published').get(lookup=None, req=req))


def assert_items_in_package(item, state, desk, stage):
    if item.get('groups'):
        terms = [{'term': {'_id': ref.get('residRef')}}
                 for ref in [ref for group in item.get('groups', [])
                             for ref in group.get('refs', []) if 'residRef' in ref]]

        query = {'or': terms}
        items = get_archive_items(query)
        assert len(items) == len(terms)
        for item in items:
            assert item.get('state') == state
            assert item.get('task', {}).get('desk') == desk
            assert item.get('task', {}).get('stage') == stage


@given('I logout')
def logout(context):
    we_have_sessions_get_id(context, '/sessions')
    step_impl_when_delete_url(context, '/auth/{}'.format(context.session_id))
    assert_200(context.response)


@then('we get "{url}" and match')
def we_get_and_match(context, url):
    url = apply_placeholders(context, url)
    response_data = get_res(url, context)
    context_data = json.loads(apply_placeholders(context, context.text))
    assert_equal(json_match(context_data, response_data), True,
                 msg=str(context_data) + '\n != \n' + str(response_data))


@then('there is no "{key}" in response')
def there_is_no_key_in_response(context, key):
    data = get_json_data(context.response)
    assert key not in data, 'key "%s" is in %s' % (key, data)


@then('there is no "{key}" in "{namespace}" preferences')
def there_is_no_key_in_preferences(context, key, namespace):
    data = get_json_data(context.response)['user_preferences']
    assert key not in data[namespace], 'key "%s" is in %s' % (key, data[namespace])
