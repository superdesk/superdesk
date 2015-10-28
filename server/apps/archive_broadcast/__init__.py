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
import superdesk
from .broadcast import ArchiveBroadcastResource, ArchiveBroadcastService, ARCHIVE_BROADCAST_NAME

logger = logging.getLogger(__name__)


def init_app(app):

    endpoint_name = ARCHIVE_BROADCAST_NAME
    service = ArchiveBroadcastService(endpoint_name, backend=superdesk.get_backend())
    ArchiveBroadcastResource(endpoint_name, app=app, service=service)

    superdesk.privilege(name=ARCHIVE_BROADCAST_NAME, label='Broadcast',
                        description='Allows user to create broadcast content.')
