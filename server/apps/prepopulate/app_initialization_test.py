from flask import current_app as app
from test_factory import SuperdeskTestCase
from .app_initialize import AppInitializeWithDataCommand
from .app_scaffold_data import AppScaffoldDataCommand
from superdesk import get_resource_service


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
            'allow_post_publish_actions': True
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
