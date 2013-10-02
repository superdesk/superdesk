
import unittest

from . import setup, app

import superdesk

class Logger(object):
    def __init__(self):
        self.called = False
        self.args = []

    def callme(self, sender, **kwargs):
        self.called = True
        self.sender = sender
        self.kwargs = kwargs

class SignalsTestCase(unittest.TestCase):

    def setUp(self):
        setup()

    def test_signals(self):
        logger = Logger()
        superdesk.connect('read:items', logger.callme)

        with app.test_request_context():
            getattr(app, 'on_fetch_resource')('items', ({}, ))

        assert logger.called, "Logger was not called"
        assert isinstance(logger.sender, superdesk.SuperdeskData), logger.sender
        assert logger.kwargs.get('docs'), logger.kwargs
