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
