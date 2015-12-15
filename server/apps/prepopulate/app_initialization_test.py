import settings
from flask import current_app as app
from test_factory import SuperdeskTestCase
from .app_initialize import AppInitializeWithDataCommand
from .app_scaffold_data import AppScaffoldDataCommand
from superdesk import get_resource_service
from apps.prepopulate.app_initialize import fillEnvironmentVariables
from unittest.mock import MagicMock


class AppInitializeWithDataCommandTestCase(SuperdeskTestCase):

    def test_app_initialization(self):
        command = AppInitializeWithDataCommand()
        result = command.run()
        self.assertEqual(result, 0)

    def test_app_initialization_multiple_loads(self):
        command = AppInitializeWithDataCommand()
        result = command.run()
        self.assertEqual(result, 0)
        result = command.run()
        self.assertEqual(result, 0)

    def data_scaffolding_test(self):
        command = AppInitializeWithDataCommand()
        result = command.run()
        self.assertEqual(result, 0)

        docs = [{
            '_id': str(x),
            'type': 'text',
            'abstract': 'test abstract {}'.format(x),
            'headline': 'test headline {}'.format(x),
            'body_html': 'test long story body {}'.format(x),
            'state': 'published'
        } for x in range(0, 40)]
        get_resource_service('published').post(docs)

        stories_per_desk = 2
        existing_desks = 18
        command = AppScaffoldDataCommand()
        result = command.run(stories_per_desk)
        self.assertEqual(result, 0)

        cursor = get_resource_service('desks').get_from_mongo(None, {})
        self.assertEqual(cursor.count(), existing_desks)

        cursor = get_resource_service('archive').get_from_mongo(None, {})
        self.assertEqual(cursor.count(), existing_desks * stories_per_desk)

    def test_app_initialization_index_creation(self):
        command = AppInitializeWithDataCommand()
        result = command.run()
        self.assertEqual(result, 0)
        result = app.data.mongo.pymongo(resource='users').db['users'].index_information()
        self.assertTrue('username_1' in result)
        self.assertTrue('first_name_1_last_name_-1' in result)
        result = app.data.mongo.pymongo(resource='archive').db['archive'].index_information()
        self.assertTrue('groups.refs.residRef_1' in result)
        self.assertTrue(result['groups.refs.residRef_1']['sparse'])

    def test_app_initialization_set_env_variables(self):
        def mock_env(variable, default):
            config = {'REUTERS_USERNAME': 'r_username', 'REUTERS_PASSWORD': 'r_password'}
            return config.get(variable, default)

        settings.env = MagicMock(side_effect=mock_env)

        item = {'username': '#ENV_REUTERS_USERNAME#', 'password': '#ENV_REUTERS_PASSWORD#'}
        crt_item = fillEnvironmentVariables(item)
        self.assertTrue(crt_item['username'] == 'r_username')
        self.assertTrue(crt_item['password'] == 'r_password')

    def test_app_initialization_notset_env_variables(self):
        def mock_env(variable, default):
            config = {'REUTERS_PASSWORD': 'r_password'}
            return config.get(variable, default)

        settings.env = MagicMock(side_effect=mock_env)

        item = {'username': '#ENV_REUTERS_USERNAME#', 'password': '#ENV_REUTERS_PASSWORD#'}
        crt_item = fillEnvironmentVariables(item)
        self.assertTrue(not crt_item)
