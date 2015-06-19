# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from apps.messaging.commands import RemoveExpiredChatSessions

from .chat_session import ChatResource, ChatService, CHAT_SESSIONS
from .messages import MessageResource, MessageService
from superdesk import get_backend, intrinsic_privilege
import logging
from superdesk.celery_app import celery

logger = logging.getLogger(__name__)


def init_app(app):
    service = ChatService(CHAT_SESSIONS, backend=get_backend())
    ChatResource(CHAT_SESSIONS, app=app, service=service)

    app.on_desk_update_or_delete -= service.on_desk_update_or_delete
    app.on_desk_update_or_delete += service.on_desk_update_or_delete

    app.on_group_update_or_delete -= service.on_group_update_or_delete
    app.on_group_update_or_delete += service.on_group_update_or_delete

    endpoint_name = 'chat_messages'
    service = MessageService(endpoint_name, backend=get_backend())
    MessageResource(endpoint_name, app=app, service=service)

    intrinsic_privilege(CHAT_SESSIONS, method=['POST', 'PATCH', 'DELETE'])
    intrinsic_privilege('chat_messages', method=['POST', 'PATCH', 'DELETE'])


@celery.task
def purge_chat_sessions():
    RemoveExpiredChatSessions().run()
