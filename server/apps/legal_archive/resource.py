# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.metadata.utils import item_url
from superdesk.resource import Resource
from superdesk.metadata.item import metadata_schema


MONGO_PREFIX = 'LEGAL_ARCHIVE'
LEGAL_ARCHIVE_NAME = 'legal_archive'
LEGAL_ARCHIVE_VERSIONS_NAME = 'legal_archive_versions'
LEGAL_PUBLISH_QUEUE_NAME = 'legal_publish_queue'


class LegalResource(Resource):
    schema = {}
    resource_methods = ['GET']
    item_methods = ['GET']
    privileges = {'GET': LEGAL_ARCHIVE_NAME}
    mongo_prefix = MONGO_PREFIX


class LegalArchiveResource(LegalResource):
    endpoint_name = LEGAL_ARCHIVE_NAME
    resource_title = endpoint_name
    schema = dict(metadata_schema)
    item_url = item_url


class LegalArchiveVersionsResource(LegalResource):
    endpoint_name = LEGAL_ARCHIVE_VERSIONS_NAME
    resource_title = endpoint_name
    doc_schema = {'_id_document': {'type': 'string'}}
    doc_schema.update(metadata_schema)
    schema = doc_schema


class LegalPublishQueueResource(LegalResource):
    endpoint_name = LEGAL_PUBLISH_QUEUE_NAME
    resource_title = endpoint_name
    doc_schema = {
        'item_id': {'type': 'string'},
        'item_version': {'type': 'string'}
    }
    doc_schema.update(metadata_schema)
    schema = doc_schema
