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
from .chat_session import CHAT_SESSIONS


class MessageResource(Resource):
    schema = {
        'message': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 500,
            'required': True,
        },
        'sender': Resource.rel('users', required=True),
        'chat_session': Resource.rel(CHAT_SESSIONS, required=True)
    }

    resource_methods = ['GET', 'POST']
    datasource = {'default_sort': [('_created', -1)]}


class MessageService(Service):
    notification_key = '*/new_message'

    def on_create(self, docs):
        for doc in docs:
            sent_user = doc.get('sender', None)
            user = get_user()
            if sent_user and str(sent_user) != str(user.get('_id')):
                message = 'Sending a message on behalf of someone else is prohibited.'
                raise SuperdeskApiError.forbiddenError(message)
            doc['sender'] = str(user.get('_id'))

            chat_session = get_resource_service(CHAT_SESSIONS).find_one(req=None, _id=doc['chat_session'])
            if chat_session is None:
                SuperdeskApiError.badRequestError('Invalid Chat Session')

    def on_created(self, docs):
        for doc in docs:
            recipients = self.resolve_message_recipients(doc)
            push_notification(self.notification_key, message=doc['message'], recipients=recipients)

    def resolve_message_recipients(self, doc):
        """
        De-normalizes the chat session if it's tied to either desk or group or both.
        :return: User ID list
        """
        recipients = set()

        chat_session = get_resource_service(CHAT_SESSIONS).find_one(req=None, _id=doc['chat_session'])

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

        return list(recipients)
