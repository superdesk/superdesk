# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from superdesk.resource import Resource
from superdesk.services import BaseService
from apps.content import metadata_schema

logger = logging.getLogger(__name__)


class PublishedItemResource(Resource):

    datasource = {
        'search_backend': 'elastic',
        'default_sort': [('_updated', -1)]
    }

    schema = {
        'item_id': Resource.rel('archive', type='string')
    }

    schema.update(metadata_schema)
    privileges = {'POST': 'publish_queue', 'PATCH': 'publish_queue'}


class PublishedItemService(BaseService):

    def on_create(self, docs):
        for doc in docs:
            doc['item_id'] = doc['_id']
            del doc['_id']
