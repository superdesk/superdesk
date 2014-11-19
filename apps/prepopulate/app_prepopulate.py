import json
import os

from superdesk import get_resource_service
import superdesk
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.tests import drop_elastic, drop_mongo
import flask


def apply_placeholders(placeholders, text):
    if not placeholders or not text:
        return text
    for tag, value in placeholders.items():
        text = text.replace(tag, value)
    return text


def set_logged_user(username, password):
    auth_token = get_resource_service('auth').find_one(username=username, req=None)
    if not auth_token:
        user = {'username': username, 'password': password}
        get_resource_service('auth').post([user])
        auth_token = get_resource_service('auth').find_one(username=username, req=None)
    flask.g.user = get_resource_service('users').find_one(req=None, username=username)
    flask.g.auth = auth_token


def get_default_user():
    user = {'username': 'test_user', 'password': 'test_password', 'is_active': True, 'needs_activation': False,
            'first_name': 'first name', 'last_name': 'last name'}
    return user


def prepopulate_data(file_name, default_user):
    placeholders = {}
    users = {default_user['username']: default_user['password']}
    default_username = default_user['username']
    file = os.path.join(superdesk.app.config.get('APP_ABSPATH'), 'apps', 'prepopulate', file_name)
    with open(file, 'rt') as app_prepopulation:
        json_data = json.loads(app_prepopulation.read())
        for item in json_data:
            service = get_resource_service(item.get('resource', None))
            username = item.get('username', None) or default_username
            set_logged_user(username, users[username])
            id_name = item.get('id_name', None)
            text = json.dumps(item.get('data', None))
            text = apply_placeholders(placeholders, text)
            data = json.loads(text)
            if item.get('resource', None) == 'users':
                users.update({data['username']: data['password']})
            try:
                ids = service.post([data])
                if id_name:
                    placeholders[id_name] = str(ids[0])
            except Exception as e:
                print('Exception:', e)


prepopulate_schema = {
    'profile': {
        'type': 'string',
        'required': False,
        'default': 'app_prepopulate_data'
    },
    'remove_first': {
        'type': 'boolean',
        'required': False,
        'default': True
    }
}


class PrepopulateResource(Resource):
    """Prepopulate application data."""
    schema = prepopulate_schema
    resource_methods = ['POST']


class PrepopulateService(BaseService):
    def create(self, docs, **kwargs):
        for doc in docs:
            if doc.get('remove_first'):
                drop_elastic(superdesk.app)
                drop_mongo(superdesk.app)
            user = get_resource_service('users').find_one(username=get_default_user()['username'], req=None)
            if not user:
                get_resource_service('users').post([get_default_user()])
            prepopulate_data(doc.get('profile') + '.json', get_default_user())
        return ['OK']


class AppPrepopulateCommand(superdesk.Command):
    def run(self):
        prepopulate_data('app_prepopulate_data.json')


superdesk.command('app:prepopulate', AppPrepopulateCommand())
