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
from apps.publish.archive_publish import ArchivePublishResource, ArchivePublishService, \
    KillPublishResource, KillPublishService, CorrectPublishResource, CorrectPublishService
from apps.publish.subscribers import SubscribersResource, SubscribersService
from apps.publish.publish_queue import PublishQueueResource, PublishQueueService
from apps.publish.published_item import PublishedItemResource, PublishedItemService
from apps.publish.commands import RemoveExpiredPublishContent  # noqa
from superdesk.celery_app import celery
from superdesk import get_backend

logger = logging.getLogger(__name__)


def init_app(app):

    endpoint_name = 'archive_publish'
    service = ArchivePublishService(endpoint_name, backend=get_backend())
    ArchivePublishResource(endpoint_name, app=app, service=service)

    endpoint_name = 'archive_kill'
    service = KillPublishService(endpoint_name, backend=get_backend())
    KillPublishResource(endpoint_name, app=app, service=service)

    endpoint_name = 'archive_correct'
    service = CorrectPublishService(endpoint_name, backend=get_backend())
    CorrectPublishResource(endpoint_name, app=app, service=service)

    endpoint_name = 'subscribers'
    service = SubscribersService(endpoint_name, backend=get_backend())
    SubscribersResource(endpoint_name, app=app, service=service)

    endpoint_name = 'publish_queue'
    service = PublishQueueService(endpoint_name, backend=get_backend())
    PublishQueueResource(endpoint_name, app=app, service=service)

    endpoint_name = 'published'
    service = PublishedItemService(endpoint_name, backend=get_backend())
    PublishedItemResource(endpoint_name, app=app, service=service)

    superdesk.privilege(name='subscribers', label='Subscribers', description='User can manage subscribers')
    superdesk.privilege(name='publish', label='Publish', description='Publish a content')
    superdesk.privilege(name='kill', label='Kill', description='Kill a published content')
    superdesk.privilege(name='correct', label='Correction', description='Correction to a published content')
    superdesk.privilege(name='publish_queue', label='Publish Queue', description='User can update publish queue')


@celery.task
def content_purge():
    RemoveExpiredPublishContent().run()
