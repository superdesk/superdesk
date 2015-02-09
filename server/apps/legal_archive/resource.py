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
from apps.archive.common import item_url
from superdesk.services import BaseService
from apps.common.models.utils import get_model
from apps.legal_archive.models.legal_archive import LegalArchiveModel
from apps.content import metadata_schema


class LegalArchiveResource(Resource):
    endpoint_name = 'legal_archive'
    schema = metadata_schema
    item_url = item_url
    resource_methods = ['GET']
    item_methods = ['GET']
    resource_title = endpoint_name


class LegalArchiveService(BaseService):
    def find_one(self, req, **lookup):
        if '_id' in lookup:
            lookup['guid'] = lookup['_id']
            del lookup['_id']
        req.sort = '-_version'
        for arg in req.args.items():
            if arg[0] == 'version':
                lookup['_version'] = arg[1]
        res = self.backend.find(self.datasource, req, lookup)
        return res[0]

    def get(self, req, lookup):
        return get_model(LegalArchiveModel).find(lookup)


class ErrorsResource(Resource):
    endpoint_name = 'errors'
    schema = {
        'resource': {'type': 'string'},
        'docs': {'type': 'list'},
        'result': {'type': 'string'}
    }
    resource_methods = []
    item_methods = []
    resource_title = endpoint_name
