# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from apps.auth.auth import SuperdeskTokenAuth
from .auth import AuthUsersResource, AuthResource  # noqa
from .sessions import SessionsResource
import superdesk
from superdesk.services import BaseService
from .db.reset_password import reset_schema  # noqa
from superdesk.celery_app import celery
import logging
from .session_purge import RemoveExpiredSessions

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
