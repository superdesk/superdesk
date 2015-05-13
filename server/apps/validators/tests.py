# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os
import json
from superdesk.tests import TestCase
from superdesk import get_resource_service
from apps.validators.command import ValidatorsPopulateCommand
from settings import URL_PREFIX


class ValidatorsPopulateTest(TestCase):

    def setUp(self):
        super(ValidatorsPopulateTest, self).setUp()
        self.filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), "validators.json")
        self.json_data = [{"_id": "publish", "schema": {"headline": {"type": "string"}}}]

        with open(self.filename, "w+") as file:
            json.dump(self.json_data, file)

    def test_populate_validators(self):
        cmd = ValidatorsPopulateCommand()
        with self.app.test_request_context(URL_PREFIX):
            cmd.run(self.filename)
            service = get_resource_service("validators")

            for item in self.json_data:
                data = service.find_one(_id=item["_id"], req=None)
                self.assertEqual(data["_id"], item["_id"])
                self.assertDictEqual(data["schema"], item["schema"])

    def tearDown(self):
        os.remove(self.filename)
        super(ValidatorsPopulateTest, self).tearDown()
