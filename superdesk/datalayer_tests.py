# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from .tests import TestCase
import superdesk


class DatalayerTestCase(TestCase):

    def test_find_all(self):
        data = {'resource': 'test', 'action': 'get'}
        with self.app.app_context():
            superdesk.get_resource_service('activity').post([data])
            self.assertEquals(1, superdesk.get_resource_service('activity').get(req=None, lookup={}).count())
