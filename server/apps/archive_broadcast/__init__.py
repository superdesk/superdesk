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
    # using events as all broadcast activity is based on the user actions
    # and will be handle by Eve. If anything is needs to be processed by backend jobs
    # then this needs to be re-visited.
    app.on_broadcast_master_updated -= service.on_broadcast_master_updated
    app.on_broadcast_master_updated += service.on_broadcast_master_updated
    app.on_broadcast_content_updated -= service.reset_broadcast_status
    app.on_broadcast_content_updated += service.reset_broadcast_status
    app.on_broadcast_master_spiked -= service.spike_broadcast_item
    app.on_broadcast_master_spiked += service.spike_broadcast_item

    superdesk.privilege(name=ARCHIVE_BROADCAST_NAME, label='Broadcast',
                        description='Allows user to create broadcast content.')
