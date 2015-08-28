# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.tests import TestCase, setup
from app import get_app


class SuperdeskTestCase(TestCase):

    def setUp(self):
        setup(self, app_factory=get_app)
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        if hasattr(self, 'ctx'):
            self.ctx.pop()
