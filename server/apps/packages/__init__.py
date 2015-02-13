# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk import get_backend
from .resource import PackageResource, PackageVersionsResource
from .service import PackageService, PackagesVersionsService


def init_app(app):
    endpoint_name = 'packages'
    service = PackageService(endpoint_name, backend=get_backend())
    PackageResource(endpoint_name, app=app, service=service)

    endpoint_name = 'packages_versions'
    service = PackagesVersionsService(endpoint_name, backend=get_backend())
    PackageVersionsResource(endpoint_name, app=app, service=service)
