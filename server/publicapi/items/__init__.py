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
from publicapi.items.resource import ItemsResource
from publicapi.items.service import ItemsService


def init_app(app):
    """Initialize the `items` API endpoint.

    :param app: the API application object
    :type app: `Eve`
    """
    endpoint_name = 'items'
    service = ItemsService(endpoint_name, backend=superdesk.get_backend())
    ItemsResource(endpoint_name, app=app, service=service)
