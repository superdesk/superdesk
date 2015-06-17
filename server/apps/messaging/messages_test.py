# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from datetime import timedelta

from apps.messaging.chat_session import CHAT_SESSIONS
from apps.messaging.commands import RemoveExpiredChatSessions
from superdesk import get_resource_service

from superdesk.tests import TestCase
from superdesk.utc import utcnow


class MessagingTestCase(TestCase):
    users = [
        {'_id': 'user1', 'needs_activation': 'false', 'is_active': 'true', 'email': 'user1@example.com',
         'username': 'user_one', 'user_type': 'administrator', 'is_enabled': 'true', 'first_name': 'User',
         'last_name': 'One'
         },
        {'_id': 'user2', 'needs_activation': 'false', 'is_active': 'true', 'email': 'user2@example.com',
         'username': 'user_two', 'user_type': 'administrator', 'is_enabled': 'true', 'first_name': 'User',
         'last_name': 'Two'
         },
        {'_id': 'user3', 'needs_activation': 'false', 'is_active': 'true', 'email': 'user3@example.com',
         'username': 'user_three', 'user_type': 'administrator', 'is_enabled': 'true', 'first_name': 'User',
         'last_name': 'Three'
         }
    ]

    desks = [{'_id': 'desk1', 'spike_expiry': 4320, 'name': 'News', 'members': [{'user': 'user1'}, {'user': 'user2'}]}]

    groups = [{'_id': 'group1', 'name': 'Administrators', 'members': [{'user': 'user3'}]}]

    def setUp(self):
        super().setUp()

        with self.app.app_context():
            self.app.data.insert('users', self.users)
            self.app.data.insert('groups', self.groups)
            self.app.data.insert('desks', self.desks)

    def test_resolve_recipients(self):
        with self.app.app_context():
            chat_session_ids = get_resource_service(CHAT_SESSIONS).post(
                [{'users': ['user2'], 'desks': ['desk1'], 'groups': ['group1']}])

            recipients = get_resource_service(CHAT_SESSIONS).resolve_message_recipients(chat_session_ids[0])

            self.assertEquals(len(recipients), 3)

    def test_if_chat_sessions_have_expired(self):
        with self.app.app_context():
            created_timestamp = utcnow() + timedelta(days=-4)
            chat_sessions = [
                {'_id': 'session1', 'users': [], '_created': created_timestamp},
                {'_id': 'session2', 'users': ['user2'], 'desks': ['desk1'], '_created': created_timestamp},
                {'_id': 'session3', 'desks': ['desk1'], '_created': utcnow()}
            ]

            chat_messages = [
                {'message': 'Test Message', 'chat_session': 'session1', '_created': created_timestamp},
                {'message': 'Test Message', 'chat_session': 'session3', '_created': utcnow()}]

            get_resource_service(CHAT_SESSIONS).post(chat_sessions)
            get_resource_service('chat_messages').post(chat_messages)

            expired_chat_sessions_service = RemoveExpiredChatSessions()
            expired_chat_sessions = expired_chat_sessions_service.get_chat_sessions(utcnow() + timedelta(days=-3))
            self.assertEquals(expired_chat_sessions.count(), 2)

            self.assertTrue(expired_chat_sessions_service.is_session_active('session3', created_timestamp))
