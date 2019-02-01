# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2016 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk

from .analysis import AnalysisResource, AnalysisService, SEMANTICS_SCHEMA


def copy_semantics(sender, item, **extra):
    archive_item = superdesk.get_resource_service('archive').find_one(req=None, _id=item['_id'])
    if archive_item and archive_item.get('semantics'):
        superdesk.get_resource_service('published').update_published_items(
            item['_id'], 'semantics', archive_item['semantics'])


def init_app(app):
    endpoint_name = 'analysis'
    service = AnalysisService(endpoint_name, backend=superdesk.get_backend())
    AnalysisResource(endpoint_name, app=app, service=service)
    superdesk.register_item_schema_field('semantics', SEMANTICS_SCHEMA, app)
    superdesk.item_published.connect(copy_semantics)
