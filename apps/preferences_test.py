
from superdesk.tests import TestCase
from superdesk import get_resource_service


class PreferencesTestCase(TestCase):

    def test_last_updated_is_up_to_date(self):
        with self.app.app_context():
            role = self.app.data.insert('roles', [{self.app.config['LAST_UPDATED']: '2014'}])
            user = {self.app.config['LAST_UPDATED']: '2013', 'role': role[0]}
            sess = {self.app.config['LAST_UPDATED']: '2012'}
            get_resource_service('preferences').enhance_document_with_user_privileges(sess, user)
            self.assertEquals('2014', sess[self.app.config['LAST_UPDATED']])
