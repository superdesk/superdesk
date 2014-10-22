import os
import unittest
from app import get_app
from pyelasticsearch import ElasticSearch
from base64 import b64encode
from flask import json
from superdesk.notification_mock import setup_notification_mock, teardown_notification_mock
from superdesk import get_resource_service
from settings import LDAP_SERVER
from unittest.mock import patch
from apps.auth.ldap.ldap import ADAuth

test_user = {'username': 'test_user', 'password': 'test_password', 'is_active': True}


def get_test_settings():
    test_settings = {}
    test_settings['ELASTICSEARCH_INDEX'] = 'sptests'
    test_settings['MONGO_DBNAME'] = 'sptests'
    test_settings['DEBUG'] = True
    test_settings['TESTING'] = True
    test_settings['BCRYPT_GENSALT_WORK_FACTOR'] = 4
    test_settings['CELERY_ALWAYS_EAGER'] = 'True'

    return test_settings


def drop_elastic(settings):
    try:
        es = ElasticSearch(settings['ELASTICSEARCH_URL'])
        es.delete_index(settings['ELASTICSEARCH_INDEX'])
    except:
        pass


def drop_mongo(app):
    with app.test_request_context():
        try:
            app.data.mongo.driver.cx.drop_database(app.config['MONGO_DBNAME'])
        except AttributeError:
            pass


def setup(context=None, config=None):
    app_config = get_test_settings()
    if config:
        app_config.update(config)

    drop_elastic(app_config)
    app = get_app(app_config)
    drop_mongo(app)

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


def setup_db_user(context, user):
    user = user or test_user
    with context.app.test_request_context():
        original_password = user['password']
        user['user_type'] = 'administrator'
        get_resource_service('users').post([user])
        user['password'] = original_password

    auth_data = json.dumps({'username': user['username'], 'password': user['password']})
    auth_response = context.client.post('/auth', data=auth_data, headers=context.headers)
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
    ad_user['user_type'] = 'administrator'

    with patch.object(ADAuth, 'authenticate_and_fetch_profile', return_value=ad_user):
        auth_data = json.dumps({'username': ad_user['username'], 'password': ad_user['password']})
        auth_response = context.client.post('/auth', data=auth_data, headers=context.headers)
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
