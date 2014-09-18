"""Superdesk push notifications"""

import logging
import asyncio

from flask import current_app as app
from flask import json
from datetime import datetime


logger = logging.getLogger(__name__)


def init_app(app):
    from autobahn.asyncio.websocket import WebSocketClientProtocol
    from autobahn.asyncio.websocket import WebSocketClientFactory
    from ws import host, port

    class Client(WebSocketClientProtocol):

        def __init__(self, *args):
            WebSocketClientProtocol.__init__(self, *args)
            self.opened = asyncio.Future()

        def notify(self, **kwargs):
            kwargs.setdefault('_created', datetime.utcnow().isoformat())
            self.sendMessage(json.dumps(kwargs).encode('utf8'))

        def onConnect(self, response):
            self.opened.set_result(None)

    factory = WebSocketClientFactory()
    factory.protocol = Client
    try:
        loop = asyncio.get_event_loop()
        coro = loop.create_connection(factory, host, port)
        _transport, client = loop.run_until_complete(coro)
        loop.run_until_complete(client.opened)
        app.notification_client = client
    except OSError:  # no ws server running
        pass


def push_notification(name, **kwargs):
    logger.info('pushing event {0} ({1})'.format(name, json.dumps(kwargs)))
    if app.notification_client:
        app.notification_client.notify(event=name, extra=kwargs)
