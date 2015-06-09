# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.resource import Resource


MONGO_PREFIX = 'LEGAL_ARCHIVE'
LEGAL_ARCHIVE_NAME = 'legal_archive'
LEGAL_ARCHIVE_VERSIONS_NAME = 'legal_archive_versions'
LEGAL_FORMATTED_ITEM_NAME = 'legal_formatted_item'
LEGAL_PUBLISH_QUEUE_NAME = 'legal_publish_queue'


class LegalArchiveResource(Resource):
    endpoint_name = LEGAL_ARCHIVE_NAME
    schema = {}
    resource_methods = ['GET']
    item_methods = ['GET']
    resource_title = endpoint_name
    internal_resource = True
    mongo_prefix = MONGO_PREFIX


class LegalArchiveVersionsResource(Resource):
    endpoint_name = LEGAL_ARCHIVE_VERSIONS_NAME
    schema = {}
    resource_methods = ['GET']
    item_methods = ['GET']
    resource_title = endpoint_name
    internal_resource = True
    mongo_prefix = MONGO_PREFIX


class LegalFormattedItemResource(Resource):
    endpoint_name = LEGAL_FORMATTED_ITEM_NAME
    schema = {}
    resource_methods = ['GET']
    item_methods = ['GET']
    resource_title = endpoint_name
    internal_resource = True
    mongo_prefix = MONGO_PREFIX


class LegalPublishQueueResource(Resource):
    endpoint_name = LEGAL_PUBLISH_QUEUE_NAME
    schema = {}
    resource_methods = ['GET']
    item_methods = ['GET']
    resource_title = endpoint_name
    internal_resource = True
    mongo_prefix = MONGO_PREFIX
