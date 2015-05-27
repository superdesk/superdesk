# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from apps.publicapi.datalayer import PublicAPIDataLayer
from superdesk.services import BaseService
from apps.publicapi.items import PublicItemsResource
from apps.publicapi.packages import PublicPackagesResource


def init_app(app):
    datalayer = PublicAPIDataLayer(app)

    endpoint_name = 'public_items'
    service = BaseService(endpoint_name, backend=datalayer)
    PublicItemsResource(endpoint_name, app=app, service=service)

    endpoint_name = 'public_packages'
    service = BaseService(endpoint_name, backend=datalayer)
    PublicPackagesResource(endpoint_name, app=app, service=service)
