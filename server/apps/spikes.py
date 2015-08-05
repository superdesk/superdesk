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
from superdesk import get_backend
from superdesk.metadata.item import metadata_schema


def init_app(app):
    endpoint_name = 'spikes'
    service = BaseService(endpoint_name, backend=get_backend())
    SpikesResource(endpoint_name, app=app, service=service)


class SpikesResource(Resource):
    schema = metadata_schema
    datasource = {
        'source': 'archive',
        'search_backend': 'elastic',
        'default_sort': [('expiry', -1)],
        'elastic_filter': {'term': {'state': 'spiked'}}
    }
    resource_methods = ['GET']
