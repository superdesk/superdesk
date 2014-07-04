
import superdesk
from superdesk.tests import TestCase


class Logger(object):

    def __init__(self):
        self.called = False
        self.args = []

    def callme(self, sender, **kwargs):
        self.called = True
        self.sender = sender
        self.kwargs = kwargs


class SignalsTestCase(TestCase):

    def test_signals(self):
        logger = Logger()
        superdesk.connect('read:items', logger.callme)

        with self.app.test_request_context():
            getattr(self.app, 'on_fetched_resource')('items', ({}, ))

        self.assertTrue(logger.called)
        self.assertIn('docs', logger.kwargs)
