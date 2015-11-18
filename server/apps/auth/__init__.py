# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import flask
import logging
import superdesk

from apps.auth.auth import SuperdeskTokenAuth
from .auth import AuthUsersResource, AuthResource  # noqa
from .sessions import SessionsResource
from superdesk.services import BaseService
from superdesk.celery_app import celery
from .session_purge import RemoveExpiredSessions
from superdesk.errors import SuperdeskApiError

logger = logging.getLogger(__name__)


def init_app(app):
    app.auth = SuperdeskTokenAuth()  # Overwrite the app default auth

    endpoint_name = 'auth_users'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    AuthUsersResource(endpoint_name, app=app, service=service)

    endpoint_name = 'sessions'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    SessionsResource(endpoint_name, app=app, service=service)


@celery.task
def session_purge():
    try:
        RemoveExpiredSessions().run()
    except Exception as ex:
        logger.error(ex)


def get_user(required=False):
    """Get user authenticated for current request.

    :param boolean required: if True and there is no user it will raise an error
    """
    user = flask.g.get('user', {})
    if '_id' not in user and required:
        raise SuperdeskApiError.notFoundError('Invalid user.')
    return user


superdesk.command('session:gc', RemoveExpiredSessions())
