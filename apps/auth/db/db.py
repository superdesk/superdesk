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
