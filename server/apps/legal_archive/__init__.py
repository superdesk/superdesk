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

from superdesk import get_backend, privilege
from .resource import LegalArchiveResource, LegalArchiveVersionsResource, LegalPublishQueueResource, \
    LEGAL_ARCHIVE_NAME, LEGAL_ARCHIVE_VERSIONS_NAME, LEGAL_PUBLISH_QUEUE_NAME
from .service import LegalArchiveService, LegalArchiveVersionsService, LegalPublishQueueService

logger = logging.getLogger(__name__)


def init_app(app):
    endpoint_name = LEGAL_ARCHIVE_NAME
    service = LegalArchiveService(endpoint_name, backend=get_backend())
    LegalArchiveResource(endpoint_name, app=app, service=service)

    endpoint_name = LEGAL_ARCHIVE_VERSIONS_NAME
    service = LegalArchiveVersionsService(endpoint_name, backend=get_backend())
    LegalArchiveVersionsResource(endpoint_name, app=app, service=service)

    endpoint_name = LEGAL_PUBLISH_QUEUE_NAME
    service = LegalPublishQueueService(endpoint_name, backend=get_backend())
    LegalPublishQueueResource(endpoint_name, app=app, service=service)

    privilege(name=LEGAL_ARCHIVE_NAME, label='Legal Archive', description='Read from legal archive')
