# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from publicapi.items.resource import ItemsResource


class PublicItemsResource(ItemsResource):
    datasource = {
        'search_backend': 'elastic',
        'source': 'items'
    }
    item_methods = ['DELETE', 'PATCH', 'GET']
    resource_methods = ['POST', 'GET']
    mongo_prefix = 'PUBLICAPI_MONGO'
    privileges = {'POST': 'publish_queue', 'DELETE': 'publish_queue', 'PATCH': 'publish_queue',
                  'DELETE': 'publish_queue'}
