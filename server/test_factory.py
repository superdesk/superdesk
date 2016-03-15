# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from flask import json
from superdesk.tests import TestCase, setup, setup_db_user, test_user, get_prefixed_url, add_to_context
from app import get_app
from unittest.mock import patch
from settings import LDAP_SERVER
from apps.ldap import ADAuth


def setup_auth_user(context, user=None):
    if LDAP_SERVER:
        setup_ad_user(context, user)
    else:
        setup_db_user(context, user)


def setup_ad_user(context, user):
    """
    Setup the AD user for the LDAP authentication.
    The method patches the authenticate_and_fetch_profile method of the ADAuth class
    :param context: test context
    :param dict user: user
    """
    ad_user = user or test_user

    '''
    This is necessary as test_user is in Global scope and del doc['password'] removes the key from test_user and
    for the next scenario, auth_data = json.dumps({'username': ad_user['username'], 'password': ad_user['password']})
    will fail as password key is removed by del doc['password']
    '''
    ad_user = ad_user.copy()
    ad_user['email'] = 'mock@mail.com.au'

    ad_user.setdefault('user_type', 'administrator')

    # ad profile to be return from the patch object
    ad_profile = {
        'email': ad_user['email'],
        'username': ad_user['username'],
        # so that test run under the administrator context.
        'user_type': ad_user.get('user_type'),
        'sign_off': ad_user.get('sign_off', 'abc'),
        'preferences': {
            'email:notification': {
                'label': 'Send notifications via email',
                'type': 'bool',
                'default': True,
                'category': 'notifications',
                'enabled': True}
        }
    }

    with patch.object(ADAuth, 'authenticate_and_fetch_profile', return_value=ad_profile):
        auth_data = json.dumps({'username': ad_user['username'], 'password': ad_user['password']})
        auth_response = context.client.post(get_prefixed_url(context.app, '/auth'),
                                            data=auth_data, headers=context.headers)
        auth_response_as_json = json.loads(auth_response.get_data())
        token = auth_response_as_json.get('token').encode('ascii')
        ad_user['_id'] = auth_response_as_json['user']

        add_to_context(context, token, ad_user)


class SuperdeskTestCase(TestCase):

    def setUp(self):
        setup(self, app_factory=get_app)
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        if hasattr(self, 'ctx'):
            self.ctx.pop()
