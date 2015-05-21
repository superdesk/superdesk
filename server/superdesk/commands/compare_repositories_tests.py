# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.tests import TestCase
from eve.utils import ParsedRequest
from superdesk import get_resource_service
from superdesk.commands.compare_repositories import CompareRepositories
from time import sleep


class RebuildIndexTestCase(TestCase):

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            data = [{'headline': 'test {}'.format(i), 'slugline': 'rebuild {}'.format(i),
                     'type': 'text' if (i % 2 == 0) else 'picture'} for i in range(1, 11)]
            get_resource_service('archive').post(data)
            sleep(1)  # sleep so Elastic has time to refresh the indexes

    def test_retrieve_items_after_index_rebuilt(self):
        with self.app.app_context():
            req = ParsedRequest()
            req.args = {}
            req.max_results = 25

            items = get_resource_service('archive').get(req, {})
            self.assertEquals(10, items.count())

            CompareRepositories().run()



