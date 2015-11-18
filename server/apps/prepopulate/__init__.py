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

from .app_prepopulate import PrepopulateService, PrepopulateResource
from .app_initialize import AppInitializeWithDataCommand  # NOQA
from .app_scaffold_data import AppScaffoldDataCommand  # NOQA


def init_app(app):
    if superdesk.app.config.get('SUPERDESK_TESTING', False):
        endpoint_name = 'prepopulate'
        service = PrepopulateService(endpoint_name, backend=superdesk.get_backend())
        PrepopulateResource(endpoint_name, app=app, service=service)

        superdesk.intrinsic_privilege(resource_name=endpoint_name, method=['POST'])
