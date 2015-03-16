# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""Superdesk push notifications"""

import logging
import asyncio

from datetime import datetime
from flask import json, current_app as app
from autobahn.asyncio.websocket import WebSocketClientProtocol
from autobahn.asyncio.websocket import WebSocketClientFactory


class Client(WebSocketClientProtocol):

    def broadcast(self, **kwargs):
        kwargs.setdefault('_created', datetime.utcnow().isoformat())
        self.msg = json.dumps(kwargs).encode('utf8')
        self.done = asyncio.Future()

    def onOpen(self):
        self.sendMessage(self.msg)
        self.sendClose()
        self.done.set_result(None)


logger = logging.getLogger(__name__)
factory = WebSocketClientFactory()
factory.protocol = Client


def send_message(**kwargs):
    """Send a message via websockets.

    It will open a new connection, send message and close it.
    """
    if app.notification_client:  # testing
        app.notification_client.notify(**kwargs)
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, app.config['WS_HOST'], app.config['WS_PORT'])
    transport, client = loop.run_until_complete(coro)
    client.broadcast(**kwargs)
    loop.run_until_complete(client.done)


def push_notification(name, **kwargs):
    """Push notification to clients.

    :param name: event name
    """
    try:
        send_message(event=name, extra=kwargs)
    except OSError:
        pass
