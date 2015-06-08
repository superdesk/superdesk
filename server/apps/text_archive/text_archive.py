
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
from apps.content import metadata_schema, not_analyzed
from apps.archive.common import aggregations, item_url
from superdesk.notification import push_notification
from apps.archive.common import get_user
import superdesk


class TextArchiveResource(Resource):
    schema = {
        'item_id': {
            'type': 'string',
            'mapping': not_analyzed
        }
    }
    schema.update(metadata_schema)
    datasource = {
        'source': 'text_archive',
        'search_backend': 'elastic',
        'aggregations': aggregations
    }
    item_url = item_url
    resource_methods = ['GET', 'POST']
    item_methods = ['GET', 'DELETE']
    privileges = {'POST': 'archive', 'DELETE': 'textarchive'}


class TextArchiveService(BaseService):

    def on_deleted(self, doc):
        user = get_user()
        push_notification('item:deleted:archive:text', item=str(doc['_id']), user=str(user.get('_id')))


superdesk.privilege(name='textarchive',
                    label='Text Archive Management',
                    description='User can remove items from the text archive.')
