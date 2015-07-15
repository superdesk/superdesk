
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
import superdesk
from superdesk.io.rfc822 import rfc822Parser
from superdesk.tests import TestCase, setup
from apps.users.services import UsersService


class rfc822TestCase(TestCase):
    filename = 'simple_email.txt'

    def setUp(self):
        setup(context=self)
        with self.app.app_context():
            # mock one user:
            user_service = UsersService(
                'users', backend=superdesk.get_backend())
            self.user_id = user_service.create([{
                'name': 'user',
                'user_type': 'administrator',
                'email': 'asender@a.com.au'
            }])[0]

            provider = {'name': 'Test'}
            dirname = os.path.dirname(os.path.realpath(__file__))
            fixture = os.path.join(dirname, 'fixtures', self.filename)
            with open(fixture, mode='rb') as f:
                bytes = f.read()
            parser = rfc822Parser()
            self.items = parser.parse_email([(1, bytes)], provider)

    def test_headline(self):
        self.assertEqual(self.items[0]['headline'], 'Test message 1234')

    def test_body(self):
        self.assertEquals(self.items[0]['body_html'].strip(), '<div>body text<br/><div>\n</div></div>')

    def test_from(self):
        self.assertEqual(self.items[0]['original_source'],
                         'a sender <asender@a.com.au>')
        self.assertEqual(self.items[0]['original_creator'], self.user_id)


class rfc822ComplexTestCase(TestCase):
    filename = 'composite_email.txt'

    def setUp(self):
        setup(context=self)
        with self.app.app_context():
            provider = {'name': 'Test'}
            dirname = os.path.dirname(os.path.realpath(__file__))
            fixture = os.path.join(dirname, 'fixtures', self.filename)
            with open(fixture, mode='rb') as f:
                bytes = f.read()
            parser = rfc822Parser()
            self.items = parser.parse_email([(1, bytes)], provider)

    def test_composite(self):
        self.assertEqual(len(self.items), 3)
        for item in self.items:
            self.assertIn('versioncreated', item)

    def test_from(self):
        self.assertEqual(self.items[0]['original_source'],
                         'someone <a@a.com.au>')
        self.assertNotIn('original_creator', self.items[0])


class rfc822OddCharSet(TestCase):
    filename = 'odd_charset_email.txt'

    def setUp(self):
        setup(context=self)
        with self.app.app_context():
            provider = {'name': 'Test'}
            dirname = os.path.dirname(os.path.realpath(__file__))
            fixture = os.path.join(dirname, 'fixtures', self.filename)
            with open(fixture, mode='rb') as f:
                bytes = f.read()
            parser = rfc822Parser()
            self.items = parser.parse_email([(1, bytes)], provider)

    def test_headline(self):
        # This tests a subject that fails to decode but we just try a string conversion
        self.assertEqual(self.items[0]['headline'], '=?windows-1252?Q?TravTalk���s_Special_for_TAAI_convention?=')

    def test_body(self):
        self.assertRegex(self.items[0]['body_html'], '<span>')


class rfc822CharSetInSubject(TestCase):
    filename = 'charset_in_subject_email.txt'

    def setUp(self):
        setup(context=self)
        with self.app.app_context():
            provider = {'name': 'Test'}
            dirname = os.path.dirname(os.path.realpath(__file__))
            fixture = os.path.join(dirname, 'fixtures', self.filename)
            with open(fixture, mode='rb') as f:
                bytes = f.read()
            parser = rfc822Parser()
            self.items = parser.parse_email([(1, bytes)], provider)

    def test_headline(self):
        # This test a subject that has a charset that decodes correctly
        self.assertEqual(self.items[0]['headline'], 'Google Apps News March 2015')
