
import unittest

from . import setup, app

import superdesk

class Logger(object):
    def __init__(self):
        self.called = False
        self.args = []

    def callme(self, *sender, **kwargs):
        self.called = True
        self.args = kwargs

class ItemsTestCase(unittest.TestCase):

    def setUp(self):
        setup()

    def test_signals(self):
        logger = Logger()
        superdesk.connect('insert', logger.callme)

        with app.test_request_context():
            app.data.insert('items', {})

        assert logger.called, "Logger was not called"
        assert logger.args.get('resource') == 'items', logger.args
