# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from apps.archive.archive import ArchiveResource, ArchiveVersionsResource

from superdesk.publish.publish_queue import PublishQueueResource
from superdesk.resource import Resource


LEGAL_ARCHIVE_NAME = 'legal_archive'
LEGAL_ARCHIVE_VERSIONS_NAME = 'legal_archive_versions'
LEGAL_PUBLISH_QUEUE_NAME = 'legal_publish_queue'


class LegalResource(Resource):
    resource_methods = ['GET']
    item_methods = ['GET']
    privileges = {'GET': LEGAL_ARCHIVE_NAME}
    mongo_prefix = 'LEGAL_ARCHIVE'


class LegalArchiveResource(LegalResource, ArchiveResource):
    endpoint_name = LEGAL_ARCHIVE_NAME
    resource_title = endpoint_name

    datasource = {'source': LEGAL_ARCHIVE_NAME}


class LegalArchiveVersionsResource(LegalResource, ArchiveVersionsResource):
    endpoint_name = LEGAL_ARCHIVE_VERSIONS_NAME
    resource_title = endpoint_name

    datasource = {'source': LEGAL_ARCHIVE_VERSIONS_NAME,
                  'projection': {'old_version': 0, 'last_version': 0}
                  }


class LegalPublishQueueResource(LegalResource, PublishQueueResource):
    endpoint_name = LEGAL_PUBLISH_QUEUE_NAME
    resource_title = endpoint_name

    item_schema = {'_subscriber_id': Resource.rel('subscribers')}
    item_schema.update(PublishQueueResource.schema)
    schema = item_schema

    datasource = {'source': LEGAL_PUBLISH_QUEUE_NAME}
