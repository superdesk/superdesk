import os
import json
from superdesk.tests import TestCase
from superdesk import get_resource_service
from .command import VocabulariesPopulateCommand
from settings import URL_PREFIX


class VocabulariesPopulateTest(TestCase):

    def setUp(self):
        super(VocabulariesPopulateTest, self).setUp()
        self.filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), "vocabularies.json")
        self.json_data = [
            {"_id": "categories",
             "items": [
                 {"name": "National", "value": "A", "is_active": True},
                 {"name": "Domestic Sports", "value": "T", "is_active": False}
             ]},
            {"_id": "newsvalue",
             "items": [
                 {"name": "1", "value": "1", "is_active": True},
                 {"name": "2", "value": "2", "is_active": True},
                 {"name": "3", "value": "3", "is_active": False}
             ]}
        ]

        with open(self.filename, "w+") as file:
            json.dump(self.json_data, file)

    def test_populate_vocabularies(self):
        cmd = VocabulariesPopulateCommand()
        with self.app.test_request_context(URL_PREFIX):
            cmd.run(self.filename)
            service = get_resource_service("vocabularies")

            for item in self.json_data:
                data = service.find_one(_id=item["_id"], req=None)
                self.assertEqual(data["_id"], item["_id"])
                self.assertListEqual(data["items"], item["items"])

    def tearDown(self):
        os.remove(self.filename)
        super(VocabulariesPopulateTest, self).tearDown()
