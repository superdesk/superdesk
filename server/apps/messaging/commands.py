# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import logging
from datetime import timedelta

from eve.utils import ParsedRequest

from apps.messaging.chat_session import CHAT_SESSIONS
from superdesk import get_resource_service
from superdesk.utc import utcnow
import superdesk

logger = logging.getLogger(__name__)


class RemoveExpiredChatSessions(superdesk.Command):
    """
    Removes expired Chat Sessions. A Chat Sessions is expired if any of the below conditions is met:
        1. If there are no recipients in the session
        2. If there are recipients but no message has been sent since 3 days
    """

    def run(self):
        expired_date_time = utcnow() + timedelta(days=-3)
        chat_sessions = self.get_chat_sessions(expired_date_time)
        if chat_sessions.count() > 0:
            for chat_session in chat_sessions:
                chat_session_id = chat_session['_id']

                if len(get_resource_service(CHAT_SESSIONS).resolve_message_recipients(chat_session_id)) == 0:
                    self.remove_chat_session(chat_session_id)
                    continue

                is_active = self.is_session_active(chat_session_id, expired_date_time)
                if not is_active:
                    self.remove_chat_session(chat_session_id)

    def get_chat_sessions(self, expired_date_time):
        req = ParsedRequest()
        req.max_results = 100
        return get_resource_service(CHAT_SESSIONS).get(req=req, lookup={'_created': {'$lte': expired_date_time}})

    def is_session_active(self, chat_session_id, expired_date_time):
        query = {'$and': [{'_created': {'$gte': expired_date_time}}, {'chat_session': chat_session_id}]}

        req = ParsedRequest()
        req.max_results = 10

        messages = get_resource_service('chat_messages').get(req=req, lookup=query)

        return messages.count() > 0

    def remove_chat_session(self, chat_session_id):
        get_resource_service('chat_messages').delete_action(lookup={'chat_session': chat_session_id})
        get_resource_service(CHAT_SESSIONS).delete_action(lookup={'_id': chat_session_id})


superdesk.command('messaging:remove_expired', RemoveExpiredChatSessions())
