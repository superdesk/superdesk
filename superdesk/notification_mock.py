from flask import json
from datetime import datetime


class ClientMock:

    def __init__(self):
        self.messages = []
        self.client = None

    def notify(self, **kwargs):
        kwargs.setdefault('_created', datetime.utcnow().isoformat())
        self.messages.append(json.dumps(kwargs).encode('utf8'))


def setup_notification_mock(context):
    clientMock = ClientMock()
    if context.app.notification_client:
        clientMock.client = context.app.notification_client
    context.app.notification_client = clientMock


def teardown_notification_mock(context):
    context.app.notification_client = context.app.notification_client.client
