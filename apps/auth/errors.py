# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from flask import json
import superdesk

logger = logging.getLogger(__name__)


class AuthRequiredError(superdesk.SuperdeskError):
    """Auth required error."""
    status_code = 401
    payload = {'auth': 1}


class AuthError(superdesk.SuperdeskError):
    """Base Auth Error"""
    status_code = 400
    payload = {'credentials': 1}


class NotFoundAuthError(AuthError):
    """Username Not Found Auth Error"""
    pass


class CredentialsAuthError(AuthError):
    """Credentials Not Match Auth Exception"""
    pass


class ForbiddenError(superdesk.SuperdeskError):
    status_code = 403


class UserInactiveError(ForbiddenError):
    """User is inactive, access restricted"""
    payload = {'is_active': False}
    message = 'Account suspended, access restricted.'


class UserImportedError(superdesk.SuperdeskError):
    payload = {'profile_to_import': 1}


def raiseCredentialsAuthError(credentials):
    logger.warning("Login failure: %s" % json.dumps(credentials))
    raise CredentialsAuthError()
