# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.errors import SuperdeskApiError
import logging
from flask import json


logger = logging.getLogger(__name__)


class UserDisabledError(SuperdeskApiError):
    """User is disabled, access restricted"""
    status_code = 403
    payload = {'is_enabled': False}
    message = 'Account is disabled, access restricted.'


class CredentialsAuthError(SuperdeskApiError):
    """Credentials Not Match Auth Exception"""

    def __init__(self, credentials, error=None):
        super().__init__(status_code=401, payload={'credentials': 1})
        logger.warning("Login failure: %s" % json.dumps(credentials))
        if error:
            logger.error("Exception occurred: {}".format(error))
