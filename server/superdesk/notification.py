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

from flask import current_app as app
from flask import json
from datetime import datetime


logger = logging.getLogger(__name__)


def init_app(app):
    from autobahn.asyncio.websocket import WebSocketClientProtocol
    from autobahn.asyncio.websocket import WebSocketClientFactory
    host = app.config['WS_HOST']
    port = app.config['WS_PORT']

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

    if app.notification_client is None:
        logger.info('Notification server is not initialized. Try to reinitialize the connection again')
        init_app(app)

    if app.notification_client is not None:
        try:
            app.notification_client.notify(event=name, extra=kwargs)
        except AttributeError:
            logger.info('Notification server is not initialized')
        except Exception as e:
            logger.exception(e)
