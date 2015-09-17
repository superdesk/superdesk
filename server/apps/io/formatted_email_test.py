# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from test_factory import SuperdeskTestCase
import os
from superdesk.io.rfc822 import rfc822Parser
from superdesk.errors import IngestEmailError


class rfc822JsonFormatter(SuperdeskTestCase):

    vocab = [{'_id': 'categories', 'items': [{'is_active': True, 'name': 'Domestic Sport', 'qcode': 's'}]}]
    desk = [{'_id': 1, 'name': 'Brisbane'}]
    user = [{'_id': 1, 'email': 'mock@mail.com.au', 'display_name': 'A Mock Up', 'sign_off': 'TA'}]

    def setUp(self):
        super().setUp()
        self.app.data.insert('vocabularies', self.vocab)
        self.app.data.insert('desks', self.desk)
        self.app.data.insert('users', self.user)
        with self.app.app_context():
            self.provider = {'name': 'Test', 'config': {'formatted': True}}

    def test_formatted_email_parser(self):
        filename = 'json-email.txt'
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.join(dirname, 'fixtures', filename)
        with open(fixture, mode='rb') as f:
            bytes = f.read()
        parser = rfc822Parser()
        self.items = parser.parse_email([(1, bytes)], self.provider)

        self.assertEqual(self.items[0]['priority'], 5)
        self.assertEqual(self.items[0]['sign_off'], 'TA')
        self.assertEqual(self.items[0]['anpa_category'], [{'qcode': 's'}])
        self.assertEqual(self.items[0]['body_html'], 'Lorem ipsum')
        self.assertEqual(self.items[0]['abstract'], 'Abstract-2')
        self.assertEqual(self.items[0]['headline'], 'Headline-2')
        self.assertEqual(self.items[0]['original_creator'], 1)
        self.assertEqual(self.items[0]['task']['desk'], 1)
        self.assertEqual(self.items[0]['urgency'], 4)
        self.assertEqual(self.items[0]['type'], 'text')
        self.assertEqual(self.items[0]['guid'], '<001a1140cd6ecd9de8051fab814d@google.com>')
        self.assertEqual(self.items[0]['original_source'], 'mock@mail.com.au')
        self.assertEqual(self.items[0]['slugline'], 'Slugline-2')
        self.assertEqual(self.items[0]['byline'], 'A Mock Up')

    def test_bad_user(self):
        filename = 'json-email-bad-user.txt'
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.join(dirname, 'fixtures', filename)
        with open(fixture, mode='rb') as f:
            bytes = f.read()
        parser = rfc822Parser()

        try:
            with self.assertRaises(IngestEmailError) as exc_context:
                self.items = parser.parse_email([(1, bytes)], self.provider)
        except:
            self.fail('Expected exception type was not raised.')

        ex = exc_context.exception
        self.assertEqual(ex.code, 6001)
