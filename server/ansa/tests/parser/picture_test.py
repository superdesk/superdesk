
import os
import flask
import unittest

from unittest.mock import MagicMock, patch
from ansa.parser.picture import PictureParser


class PictureParserTestCase(unittest.TestCase):

    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.media = MagicMock()
        self.app.config.update({
            'SERVER_DOMAIN': 'test',
            'RENDITIONS': {'picture': {}},
        })

    @patch('superdesk.io.feed_parsers.image_iptc.get_renditions_spec', return_value={})
    @patch('superdesk.io.feed_parsers.image_iptc.generate_renditions', return_value={})
    def test_parse_guid_filename(self, get_renditions_spec, generate_renditions):
        parser = PictureParser()
        with self.app.app_context():
            path = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'fixture.jpg')
            item = parser.parse(path)
            self.assertEqual('fixture.jpg', item['guid'])
            self.assertEqual('fixture.jpg', item['uri'])
