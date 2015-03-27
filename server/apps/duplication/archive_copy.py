# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from flask import request

from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError
from superdesk.notification import push_notification
from superdesk.resource import Resource
from superdesk.services import BaseService
from apps.archive.common import item_url
from apps.archive.archive import SOURCE as ARCHIVE


class CopyResource(Resource):
    endpoint_name = 'copy'
    resource_title = endpoint_name

    # Eve needs schema definition even if all the properties are optional.
    schema = {
        'desk': Resource.rel('desks', False, required=False)
    }

    url = 'archive/<{0}:guid>/copy'.format(item_url)

    resource_methods = ['POST']
    item_methods = []


class CopyService(BaseService):
    def create(self, docs, **kwargs):
        guid_of_item_to_be_copied = request.view_args['guid']

        guid_of_copied_items = []

        for doc in docs:
            archive_service = get_resource_service(ARCHIVE)

            archived_doc = archive_service.find_one(req=None, _id=guid_of_item_to_be_copied)
            if not archived_doc:
                raise SuperdeskApiError.notFoundError('Fail to found item with guid: %s' %
                                                      guid_of_item_to_be_copied)

            current_desk_of_item = archived_doc.get('task', {}).get('desk')
            if current_desk_of_item:
                raise SuperdeskApiError.preconditionFailedError(message='Copy is not allowed on items in a desk.')

            new_guid = archive_service.duplicate_content(archived_doc)
            guid_of_copied_items.append(new_guid)

        if kwargs.get('notify', True):
            push_notification('item:copy', copied=1)

        return guid_of_copied_items
