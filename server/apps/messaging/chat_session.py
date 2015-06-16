# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from apps.archive.common import get_user

from superdesk import Resource, Service
from superdesk.errors import SuperdeskApiError

CHAT_SESSIONS = 'chat_sessions'


class ChatResource(Resource):
    schema = {
        'creator': Resource.rel('users', required=False),
        'users': {'type': 'list', 'schema': Resource.rel('users', required=True)},
        'desks': {'type': 'list', 'schema': Resource.rel('desks', required=True)},
        'groups': {'type': 'list', 'schema': Resource.rel('groups', required=True)}
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
