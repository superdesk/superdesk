
from superdesk.macros import macros
from superdesk.tests import TestCase


class MacrosTestCase(TestCase):

    def test_register(self):
        with self.app.app_context():
            macros.register(name='test')
            self.assertEqual(1, len(macros))
            self.assertIn('test', macros)
