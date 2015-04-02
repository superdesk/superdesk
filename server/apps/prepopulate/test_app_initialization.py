from superdesk.tests import TestCase
from .app_initialize import AppInitializeWithDataCommand


class AppInitializeWithDataCommandTestCase(TestCase):

    def setUp(self):
        super().setUp()

    def test_app_initialization(self):
        with self.app.app_context():
            command = AppInitializeWithDataCommand()
            result = command.run()
            self.assertEquals(result, 0)
