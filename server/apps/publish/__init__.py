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
from apps.publish.destination_groups import DestinationGroupsResource, DestinationGroupsService
from apps.publish.output_channels import OutputChannelsResource, OutputChannelsService
from apps.publish.subscribers import SubscribersResource, SubscribersService
from apps.publish.publish_queue import PublishQueueResource, PublishQueueService
from apps.publish.formatted_item import FormattedItemResource, FormattedItemService
from apps.publish.published_item import PublishedItemResource, PublishedItemService

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

    endpoint_name = 'formatted_item'
    service = FormattedItemService(endpoint_name, backend=get_backend())
    FormattedItemResource(endpoint_name, app=app, service=service)

    endpoint_name = 'published'
    service = PublishedItemService(endpoint_name, backend=get_backend())
    PublishedItemResource(endpoint_name, app=app, service=service)

    endpoint_name = 'output_channels'
    service = OutputChannelsService(endpoint_name, backend=get_backend())
    OutputChannelsResource(endpoint_name, app=app, service=service)

    endpoint_name = 'destination_groups'
    service = DestinationGroupsService(endpoint_name, backend=get_backend())
    DestinationGroupsResource(endpoint_name, app=app, service=service)

    superdesk.privilege(name='publish', label='Publish', description='Publish a content')
    superdesk.privilege(name='destination_groups', label='Destination Groups',
                        description='User can manage destination groups')
    superdesk.privilege(name='output_channels', label='Output Channels',
                        description='User can manage output channels')
    superdesk.privilege(name='subscribers', label='Subscribers',
                        description='User can manage subscribers')
    superdesk.privilege(name='publish_queue', label='Publish Queue',
                        description='User can update publish queue')
    superdesk.privilege(name='output_channel_seq_num_settings', label='Update Output Channel Sequence Number Settings',
                        description='User can update Update Output Channel Sequence Number Settings.')
