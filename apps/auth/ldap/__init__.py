# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
from apps.auth import AuthResource
from .ldap import ADAuthService, ADAuth, ImportUserProfileResource, ImportUserProfileService  # noqa
from .commands import ImportUserProfileFromADCommand  # noqa


def init_app(app):
    endpoint_name = 'auth'
    service = ADAuthService(endpoint_name, backend=superdesk.get_backend())
    AuthResource(endpoint_name, app=app, service=service)

    endpoint_name = ImportUserProfileResource.url
    service = ImportUserProfileService(endpoint_name, backend=superdesk.get_backend())
    ImportUserProfileResource(endpoint_name, app=app, service=service)
