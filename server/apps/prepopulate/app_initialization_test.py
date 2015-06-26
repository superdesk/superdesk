from superdesk.tests import TestCase
from .app_initialize import AppInitializeWithDataCommand
from .app_scaffold_data import AppScaffoldDataCommand
from superdesk import get_resource_service


class AppInitializeWithDataCommandTestCase(TestCase):

    def setUp(self):
        super().setUp()

    def test_app_initialization(self):
        with self.app.app_context():
            command = AppInitializeWithDataCommand()
            result = command.run()
            self.assertEquals(result, 0)

    def test_app_initialization_multiple_loads(self):
        with self.app.app_context():
            command = AppInitializeWithDataCommand()
            result = command.run()
            self.assertEquals(result, 0)
            result = command.run()
            self.assertEquals(result, 0)

    def data_scaffolding_test(self):
        with self.app.app_context():
            command = AppInitializeWithDataCommand()
            result = command.run()
            self.assertEquals(result, 0)

            service = get_resource_service('text_archive')
            docs = [{
                'type': 'text',
                'abstract': 'test abstract {}'.format(x),
                'headline': 'test headline {}'.format(x),
                'body_html': 'test long story body {}'.format(x)
            } for x in range(0, 40)]
            service.post(docs)

            stories_per_desk = 2
            existing_desks = 18
            command = AppScaffoldDataCommand()
            result = command.run(stories_per_desk)
            self.assertEquals(result, 0)

            cursor = get_resource_service('desks').get_from_mongo(None, {})
            self.assertEquals(cursor.count(), existing_desks)

            cursor = get_resource_service('archive').get_from_mongo(None, {})
            self.assertEquals(cursor.count(), existing_desks * stories_per_desk)
