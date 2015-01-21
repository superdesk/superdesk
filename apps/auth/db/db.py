# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import bcrypt
from apps.auth.service import AuthService
from superdesk import get_resource_service
from superdesk.errors import CredentialsAuthError
from apps.common.components.utils import get_component
from apps.item_lock.components.item_lock import ItemLock


class DbAuthService(AuthService):

    def authenticate(self, credentials):
        user = get_resource_service('auth_users').find_one(req=None, username=credentials.get('username'))
        if not user:
            raise CredentialsAuthError(credentials)

        password = credentials.get('password').encode('UTF-8')
        hashed = user.get('password').encode('UTF-8')

        if not (password and hashed):
            raise CredentialsAuthError(credentials)

        try:
            rehashed = bcrypt.hashpw(password, hashed)
            if hashed != rehashed:
                raise CredentialsAuthError(credentials)
        except ValueError:
            raise CredentialsAuthError(credentials)

        return user

    def on_deleted(self, doc):
        '''
        :param doc: A deleted auth doc AKA a session
        :return:
        '''
        print('deleting locks for session {}'.format(doc['_id']))
        # need to relinquish all locks for this session
        get_component(ItemLock).unlock_session(doc['user'], doc['_id'])

    def delete_all(self, query):
        '''
        :param query: a query that will find all sessions (auth records) that match the query
        :return:
        '''
        print('delete sessions matching {}'.format(query))
        sessions = get_resource_service('auth').get(req=None, lookup=query)
        for session in sessions:
            print('session {}'.format(session['_id']))
            get_resource_service('auth').delete_action({'_id': str(session['_id'])})
