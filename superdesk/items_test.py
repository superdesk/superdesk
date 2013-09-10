
import blinker
import unittest

from superdesk.testing import setup

class Logger(object):
    def __init__(self):
        self.called = False
        self.args = []

    def callme(self, *args):
        self.called = True
        self.args = args

class ItemsTestCase(unittest.TestCase):

    def setUp(self):
        setup(self)

    def test_signals(self):
        logger = Logger()
        save_item_signal = blinker.signal('item:save')
        save_item_signal.connect(logger.callme)

        from superdesk import items, app
        with app.test_request_context():
            items.save_item({})

        assert logger.called, "Logger was not called"
        assert logger.args[0].get('guid'), "Event arg has no guid"
