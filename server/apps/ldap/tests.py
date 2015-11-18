# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from unittest import mock
from unittest.mock import MagicMock
from apps.auth.errors import CredentialsAuthError
from settings import LDAP_SERVER
from superdesk.errors import SuperdeskApiError
from test_factory import SuperdeskTestCase
from superdesk import get_resource_service
from .commands import ImportUserProfileFromADCommand

if LDAP_SERVER:
    def get_mock_connection():
        """
        Create a mock ldap connection object.
        :return {object}: mock ldap connection object.
        """
        connection = MagicMock()
        connection.search(return_value=True)
        connection.response = [
            {
                'attributes': {
                    'sn': ['Bar'],
                    'givenName': ['Foo'],
                    'displayName': ['Foo Bar'],
                    'ipPhone': '+1234567890',
                    'email': 'foo@bar.com'
                }
            }
        ]

        return connection

    @mock.patch('apps.ldap.ldap.Connection', return_value=get_mock_connection())
    class ImportUsersTestCase(SuperdeskTestCase):
        """
        for testing import user using ldap.
        """
        def test_import_user_using_command(self, mock_ldap_connection):
            user = {'username': 'user', 'password': 'pwd', 'user_to_import': 'barf'}
            cmd = ImportUserProfileFromADCommand()

            cmd.run(user['username'], user['password'], user['user_to_import'])
            auth_user = get_resource_service('auth').authenticate({'username': 'barf', 'password': 'dummy'})
            self.assertEqual(auth_user['username'], user['user_to_import'])

            cmd.run(user['username'], user['password'], 'BARF')
            auth_user2 = get_resource_service('auth').authenticate({'username': 'barf', 'password': 'dummy'})
            self.assertEqual(auth_user2['username'], user['user_to_import'])

            self.assertEqual(auth_user2['_id'], auth_user['_id'])

        @mock.patch('apps.ldap.ldap.get_user', return_value={'username': 'user'})
        def test_import_profile_for_already_imported_user_raises_exception(self, mock_ldap_connection, mock_get_user):
            with self.assertRaises(SuperdeskApiError) as context:
                service = get_resource_service('import_profile')
                doc = {'username': 'user', 'password': 'pwd', 'profile_to_import': 'barf'}
                users = service.post([doc])
                self.assertIsNotNone(users)
                self.assertEqual(len(users), 1)
                doc = {'username': 'user', 'password': 'pwd', 'profile_to_import': 'BARF '}
                service.post([doc])

            ex = context.exception
            self.assertEqual(ex.message, 'User already exists in the system.')
            self.assertEqual(ex.status_code, 400)
            self.assertDictEqual(ex.payload, {'profile_to_import': 1})

        @mock.patch('apps.ldap.ldap.get_user', return_value={'username': 'user1'})
        def test_import_user_by_not_logged_in_user_raises_exception(self, mock_ldap_connection, mock_get_user):
            with self.assertRaises(SuperdeskApiError) as context:
                service = get_resource_service('import_profile')
                doc = {'username': 'user', 'password': 'pwd', 'profile_to_import': 'barf'}
                service.post([doc])

            ex = context.exception
            self.assertEqual(ex.message, 'Invalid Credentials.')
            self.assertEqual(ex.status_code, 403)
            self.assertDictEqual(ex.payload, {'credentials': 1})

        @mock.patch('apps.ldap.ldap.ADAuth.authenticate_and_fetch_profile',
                    side_effect=CredentialsAuthError(credentials={'username': 'test'}, error='test'))
        @mock.patch('apps.ldap.ldap.get_user', return_value={'username': 'user'})
        def test_user_import_profile_with_invalid_credentials(self, mock_ldap_connection, mock_auth, mock_get_user):
                with self.assertRaises(SuperdeskApiError) as context:
                    service = get_resource_service('import_profile')
                    doc = {'username': 'user', 'password': 'pwd', 'profile_to_import': 'barf'}
                    service.post([doc])

                ex = context.exception
                self.assertEqual(ex.message, 'Invalid Credentials.')
                self.assertEqual(ex.status_code, 403)
                self.assertDictEqual(ex.payload, {'credentials': 1})
