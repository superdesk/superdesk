
from superdesk.macros import macros
from superdesk.tests import TestCase


class MacrosTestCase(TestCase):

    def test_register(self):
        with self.app.app_context():
            macros.register(name='test')
            self.assertIn('test', macros)

    def test_load_modules(self):
        with self.app.app_context():
            self.assertIn('usd_to_aud', macros)
            self.assertNotIn('foo name', macros)
