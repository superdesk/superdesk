# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from eve.utils import config

from apps.archive.common import get_user
from superdesk import Resource, Service, get_resource_service
from superdesk.errors import SuperdeskApiError
from superdesk.notification import push_notification

CHAT_SESSIONS = 'chat_sessions'


class ChatResource(Resource):
    schema = {
        'creator': Resource.rel('users', required=False),
        'users': {'type': 'list', 'schema': Resource.rel('users', required=True)},
        'desks': {'type': 'list', 'schema': Resource.rel('desks', required=True)},
        'groups': {'type': 'list', 'schema': Resource.rel('groups', required=True)},
        'recipients': {'type': 'list', 'schema': Resource.rel('users', required=True)}
    }
    resource_methods = ['GET', 'POST']
    datasource = {'default_sort': [('_created', -1)]}


class ChatService(Service):

    def on_create(self, docs):
        for doc in docs:
            sent_user = doc.get('creator', None)
            user = get_user()
            if sent_user and sent_user != str(user.get('_id')):
                message = 'Creating a chat session on behalf of someone else is prohibited.'
                raise SuperdeskApiError.forbiddenError(message)
            creator = str(user.get('_id'))
            doc['creator'] = creator
            doc['recipients'] = list(self.resolve_message_recipients(chat_session=doc)) + [creator]

    def on_created(self, docs):
        for doc in docs:
            for recipient in doc['recipients']:
                push_notification('messaging:user:added', user_id=recipient, chat_session_id=str(doc[config.ID_FIELD]))

    def on_update(self, updates, original):
        self._populate_users_desks_groups_recipients(original, updates)

    def on_updated(self, updates, original):
        new_recipients = list(set(updates.get('recipients')) - set(original.get('recipients')))

        for recipient in new_recipients:
            push_notification('messaging:user:added', user_id=recipient, chat_session_id=str(original[config.ID_FIELD]))

    def on_delete(self, doc):
        get_resource_service('chat_messages').delete_action(lookup={'chat_session': doc[config.ID_FIELD]})

    def on_desk_update_or_delete(self, desk_id, event='update'):
        """
        Invoked when a Desk is updated/deleted. Fetches Chat Session(s) which the desk identified by desk_id
        is part of. For each Chat Session performs one of the below:
            (1) updates the recipients if the desk is updated
            (2) kills the chat sessions if the desk is deleted
        """

        chat_sessions = self.get(req=None, lookup={'desks': desk_id})
        for chat_session in chat_sessions:
            if event == 'update':
                updates = {'desks': [desk for desk in chat_session['desks'] if str(desk) != str(desk_id)]}
                self._update_chat_session(chat_session, updates)
            else:
                self._kill_chat_session(chat_session, 'Desk(s)')

    def on_group_update_or_delete(self, group_id, event='update'):
        """
        Invoked when a Group is updated/deleted. Fetches Chat Session(s) which the group identified by group_id
        is part of. For each Chat Session performs one of the below:
            (1) updates the recipients if the group is updated
            (2) kills the chat sessions if the group is deleted
        """

        chat_sessions = self.get(req=None, lookup={'groups': group_id})
        for chat_session in chat_sessions:
            if event == 'update':
                updates = {'groups': [group for group in chat_session['groups'] if str(group) != str(group_id)]}
                self._update_chat_session(chat_session, updates)
            else:
                self._kill_chat_session(chat_session, 'Group(s)')

    def resolve_message_recipients(self, chat_session_id=None, chat_session=None):
        """
        De-normalizes the chat session if it's tied to either desk or group or both.
        :return: User ID list
        """

        if chat_session_id is None and chat_session is None:
            raise SuperdeskApiError.badRequestError(
                "Invalid Arguments. Either Chat Session or it's identifier is needed to proceed further.")

        recipients = set()

        if chat_session is None:
            chat_session = get_resource_service(CHAT_SESSIONS).find_one(req=None, _id=chat_session_id)

        if len(chat_session.get('users', [])):
            recipients.update([str(user) for user in chat_session['users']])

        if len(chat_session.get('desks', [])):
            query = {'$and': [{config.ID_FIELD: {'$in': chat_session['desks']}}]}
            desks = list(get_resource_service('desks').get(req=None, lookup=query))

            recipients.update([str(member['user']) for desk in desks for member in desk.get('members', [])])

        if len(chat_session.get('groups', [])):
            query = {'$and': [{config.ID_FIELD: {'$in': chat_session['groups']}}]}
            groups = list(get_resource_service('groups').get(req=None, lookup=query))

            recipients.update([str(member['user']) for group in groups for member in group.get('members', [])])

        return recipients

    def _populate_users_desks_groups_recipients(self, source, destination):
        """
        Checks if destination has properties - users, desks, groups. If not the properties are copied from source and
        resolves recipients for the destination.
        """

        if 'users' not in destination and source.get('users'):
            destination['users'] = source.get('users')
        if 'desks' not in destination and source.get('desks'):
            destination['desks'] = source.get('desks')
        if 'groups' not in destination and source.get('groups'):
            destination['groups'] = source.get('groups')

        destination['recipients'] = \
            list(self.resolve_message_recipients(chat_session=destination)) + [source.get('creator')]

    def _update_chat_session(self, chat_session, updates):
        self._populate_users_desks_groups_recipients(chat_session, updates)
        self.update(chat_session[config.ID_FIELD, updates, chat_session])

    def _kill_chat_session(self, chat_session, type_):
        self.delete_action(lookup={config.ID_FIELD: chat_session[config.ID_FIELD]})
        push_notification("chat_session_end", message='Chat Session Ends as the %s is removed' % type_,
                          recipients=chat_session['recipients'])
