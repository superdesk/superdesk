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
from .utils import last_updated
from .utc import utcnow


class UtilsTestCase(TestCase):

    def test_last_updated(self):
        with self.app.app_context():
            self.assertEquals('2012', last_updated(
                {self.app.config['LAST_UPDATED']: '2011'},
                {self.app.config['LAST_UPDATED']: '2012'},
                {self.app.config['LAST_UPDATED']: '2010'},
                {},
                None
            ))

            now = utcnow()
            self.assertGreaterEqual(last_updated(), now)
