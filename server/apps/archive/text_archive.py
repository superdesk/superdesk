
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
from superdesk.services import BaseService
from apps.content import metadata_schema
from .common import aggregations, item_url
from superdesk import intrinsic_privilege


class TextArchiveResource(Resource):
    schema = {}
    schema.update(metadata_schema)
    datasource = {
        'source': 'text_archive',
        'search_backend': 'elastic',
        'aggregations': aggregations
    }
    item_url = item_url
    resource_methods = ['GET', 'POST']


class TextArchiveService(BaseService):
    pass


intrinsic_privilege('text_archive', method=['GET', 'POST'])
