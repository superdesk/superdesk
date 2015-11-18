# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
from superdesk.resource import Resource
from superdesk.services import BaseService
from apps.comments import CommentsService, CommentsResource, comments_schema
from superdesk.errors import SuperdeskApiError


comments_schema = dict(comments_schema)
comments_schema.update({'item': Resource.rel('archive', True, True, type='string')})


class ItemCommentsResource(CommentsResource):
    schema = comments_schema
    resource_methods = ['GET', 'POST', 'DELETE']
    datasource = {'default_sort': [('_created', -1)]}
    privileges = {'POST': 'archive', 'DELETE': 'archive'}


class ItemCommentsService(CommentsService):
    notification_key = 'item:comment'


class ItemCommentsSubResource(Resource):
    url = 'archive/<path:item>/comments'
    schema = comments_schema
    datasource = {'source': 'item_comments'}
    resource_methods = ['GET']


class ItemCommentsSubService(BaseService):

    def check_item_valid(self, item_id):
        item = superdesk.get_resource_service('archive').find_one(req=None, _id=item_id)
        if not item:
            msg = 'Invalid content item ID provided: %s' % item_id
            raise SuperdeskApiError.notFoundError(msg)

    def get(self, req, lookup):
        self.check_item_valid(lookup.get('item'))
        return super().get(req, lookup)
