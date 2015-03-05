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
from superdesk.io.rfc822 import rfc822Parser
from superdesk.tests import TestCase
from superdesk.tests import setup


class rfc822TestCase(TestCase):
    filename = 'simple_email.txt'

    def setUp(self):
        setup(context=self)
        with self.app.app_context():
            dirname = os.path.dirname(os.path.realpath(__file__))
            fixture = os.path.join(dirname, 'fixtures', self.filename)
            with open(fixture, mode='rb') as f:
                bytes = f.read()
            parser = rfc822Parser()
            self.items = parser.parse_email([(1, bytes)])

    def test_headline(self):
        self.assertEqual(self.items[0]['headline'], 'Test message 1234')

    def test_body(self):
        self.assertEquals(self.items[0]['body_html'].strip(), '<div dir="ltr">body text<br clear="all"><div>')


class rfc822ComplexTestCase(TestCase):
    filename = 'composite_email.txt'

    def setUp(self):
        setup(context=self)
        with self.app.app_context():
            dirname = os.path.dirname(os.path.realpath(__file__))
            fixture = os.path.join(dirname, 'fixtures', self.filename)
            with open(fixture, mode='rb') as f:
                bytes = f.read()
            parser = rfc822Parser()
            self.items = parser.parse_email([(1, bytes)])

    def test_composite(self):
        self.assertEqual(len(self.items), 3)
