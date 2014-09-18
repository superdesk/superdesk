
import os
import unittest
from app import get_app
from pyelasticsearch import ElasticSearch
from base64 import b64encode
from flask import json
from superdesk.notification_mock import setup_notification_mock,\
    teardown_notification_mock

test_user = {'username': 'test_user', 'password': 'test_password'}


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
    if config:
        config.update(get_test_settings())
    else:
        config = get_test_settings()

    drop_elastic(config)
    app = get_app(config)

    drop_mongo(app)
    if context:
        context.app = app
        context.client = app.test_client()


def setup_auth_user(context, user=None):
    user = user or test_user
    with context.app.test_request_context():
        original_password = user['password']
        context.app.data.insert('users', [user])
        user['password'] = original_password
    auth_data = json.dumps({'username': user['username'], 'password': user['password']})
    auth_response = context.client.post('/auth', data=auth_data, headers=context.headers)
    token = json.loads(auth_response.get_data()).get('token').encode('ascii')
    context.headers.append(('Authorization', b'basic ' + b64encode(token + b':')))
    context.user = user


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
