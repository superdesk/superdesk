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
from .archive_copy import CopyService, CopyResource
from .archive_duplication import DuplicateService, DuplicateResource
from .archive_fetch import FetchResource, FetchService
from .archive_move import MoveResource, MoveService
import superdesk


logger = logging.getLogger(__name__)


def init_app(app):
    endpoint_name = 'fetch'
    service = FetchService(endpoint_name, backend=superdesk.get_backend())
    FetchResource(endpoint_name, app=app, service=service)

    endpoint_name = 'duplicate'
    service = DuplicateService(endpoint_name, backend=superdesk.get_backend())
    DuplicateResource(endpoint_name, app=app, service=service)

    endpoint_name = 'copy'
    service = CopyService(endpoint_name, backend=superdesk.get_backend())
    CopyResource(endpoint_name, app=app, service=service)

    endpoint_name = 'move'
    service = MoveService(endpoint_name, backend=superdesk.get_backend())
    MoveResource(endpoint_name, app=app, service=service)

    superdesk.privilege(name='fetch', label='Fetch Content To a Desk', description='Fetch Content to a Desk')
    superdesk.privilege(name='move', label='Move Content to another desk', description='Move Content to another desk')
    superdesk.privilege(name='duplicate', label='Duplicate Content within a Desk',
                        description='Duplicate Content within a Desk')

    superdesk.intrinsic_privilege('copy', method=['POST'])
