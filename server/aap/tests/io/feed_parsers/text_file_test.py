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
from test_factory import SuperdeskTestCase
from aap.io.feed_parsers.text_file import TextFileParser


class TextFileTestCase(SuperdeskTestCase):

    filename = 'CRN2016427R1.tst'

    def setUp(self):
        super().setUp()
        dirname = os.path.dirname(os.path.realpath(__file__))
        self.fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        self.provider = {'name': 'Test'}

    def test_headline(self):
        item = TextFileParser().parse(self.fixture, self.provider)
        self.assertEqual(item['headline'], 'Cranbourne, Wednesday 27 Apr 2016')
        self.assertEqual(item['format'], 'preserved')
