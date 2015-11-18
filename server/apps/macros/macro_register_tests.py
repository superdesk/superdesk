# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from .macro_register import macros
from test_factory import SuperdeskTestCase


class MacrosTestCase(SuperdeskTestCase):

    def test_register(self):
        with self.app.app_context():
            macros.register(name='test')
            self.assertIn('test', macros)

    def test_load_modules(self):
        with self.app.app_context():
            self.assertIn('usd_to_aud', macros)
            self.assertNotIn('foo name', macros)
