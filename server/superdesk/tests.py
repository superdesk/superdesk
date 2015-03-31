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
import unittest
import elasticsearch
from app import get_app
from base64 import b64encode
from flask import json
from superdesk.notification_mock import setup_notification_mock, teardown_notification_mock
from superdesk import get_resource_service
from settings import LDAP_SERVER, ELASTICSEARCH_URL
from unittest.mock import patch
from apps.auth.ldap.ldap import ADAuth
from eve_elastic import get_es, get_indices

test_user = {
    'username': 'test_user',
    'password': 'test_password',
    'is_active': True,
    'is_enabled': True,
    'needs_activation': False,
    'email': 'behave_test@sourcefabric.org',
    'preferences': {
        'email:notification': {
            'label': 'Send notifications via email',
            'type': 'bool',
            'default': True,
            'category': 'notifications',
            'enabled': True}
    }

}


def get_test_settings():
    test_settings = {}
    test_settings['ELASTICSEARCH_URL'] = ELASTICSEARCH_URL
    test_settings['ELASTICSEARCH_INDEX'] = 'sptest'
    test_settings['MONGO_DBNAME'] = 'sptests'
    test_settings['LEGAL_ARCHIVE_DBNAME'] = 'sptests_legal'
    test_settings['DEBUG'] = True
    test_settings['TESTING'] = True
    test_settings['SUPERDESK_TESTING'] = True
    test_settings['BCRYPT_GENSALT_WORK_FACTOR'] = 4
    test_settings['CELERY_ALWAYS_EAGER'] = 'True'
    test_settings['CONTENT_EXPIRY_MINUTES'] = 99

    return test_settings


def drop_elastic(app):
    with app.app_context():
        try:
            es = get_es(app.config['ELASTICSEARCH_URL'])
            get_indices(es).delete(app.config['ELASTICSEARCH_INDEX'])
        except elasticsearch.exceptions.NotFoundError:
            pass


def drop_mongo(app):
    with app.app_context():
        try:
            app.data.mongo.pymongo().cx.drop_database(app.config['MONGO_DBNAME'])
            app.data.mongo.pymongo().cx.drop_database(app.config['LEGAL_ARCHIVE_DBNAME'])
        except AttributeError:
            pass


def setup(context=None, config=None):
    app_config = get_test_settings()
    if config:
        app_config.update(config)

    app = get_app(app_config)
    drop_elastic(app)
    drop_mongo(app)

    # create index again after dropping it
    app.data.elastic.init_app(app)

    if context:
        context.app = app
        context.client = app.test_client()


def setup_auth_user(context, user=None):
    if LDAP_SERVER:
        setup_ad_user(context, user)
    else:
        setup_db_user(context, user)


def add_to_context(context, token, user):
    context.headers.append(('Authorization', b'basic ' + b64encode(token + b':')))
    context.user = user
    set_placeholder(context, 'CONTEXT_USER_ID', str(user.get('_id')))


def set_placeholder(context, name, value):
    old_p = getattr(context, 'placeholders', None)
    if not old_p:
        context.placeholders = dict()
    context.placeholders[name] = value


def get_prefixed_url(current_app, endpoint):
    if endpoint.startswith('http://'):
        return endpoint

    endpoint = endpoint if endpoint.startswith('/') else ('/' + endpoint)
    url = current_app.config['URL_PREFIX'] + endpoint
    return url


def setup_db_user(context, user):
    user = user or test_user
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        original_password = user['password']

        if user.get('user_type') is None:
            user['user_type'] = 'administrator'

        if not get_resource_service('users').find_one(username=user['username'], req=None):
            get_resource_service('users').post([user])

        user['password'] = original_password
        auth_data = json.dumps({'username': user['username'], 'password': user['password']})
        auth_response = context.client.post(get_prefixed_url(context.app, '/auth'),
                                            data=auth_data, headers=context.headers)

        token = json.loads(auth_response.get_data()).get('token').encode('ascii')
        add_to_context(context, token, user)


def setup_ad_user(context, user):
    ad_user = user or test_user

    '''
    This is necessary as test_user is in Global scope and del doc['password'] removes the key from test_user and
    for the next scenario, auth_data = json.dumps({'username': ad_user['username'], 'password': ad_user['password']})
    will fail as password key is removed by del doc['password']
    '''
    ad_user = ad_user.copy()
    ad_user['email'] = 'mock@mail.com.au'

    if ad_user.get('user_type') is None:
        ad_user['user_type'] = 'administrator'

    with patch.object(ADAuth, 'authenticate_and_fetch_profile', return_value=ad_user):
        auth_data = json.dumps({'username': ad_user['username'], 'password': ad_user['password']})
        auth_response = context.client.post(get_prefixed_url(context.app, '/auth'),
                                            data=auth_data, headers=context.headers)
        auth_response_as_json = json.loads(auth_response.get_data())
        token = auth_response_as_json.get('token').encode('ascii')
        ad_user['_id'] = auth_response_as_json['user']

        add_to_context(context, token, ad_user)


def setup_notification(context):
    setup_notification_mock(context)


def teardown_notification(context):
    teardown_notification_mock(context)


class TestCase(unittest.TestCase):
    def setUp(self):
        setup(self)

    def get_fixture_path(self, filename):
        rootpath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(rootpath, 'features', 'steps', 'fixtures', filename)
