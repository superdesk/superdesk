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

from superdesk import get_resource_service, Service, Resource
from .archive_composite import PackageService
from apps.archive.common import item_url
from apps.archive.archive import SOURCE as ARCHIVE
import logging

logger = logging.getLogger(__name__)


class ArchiveLinkResource(Resource):
    endpoint_name = 'archive_link'
    resource_title = endpoint_name

    schema = {
        'link_id': Resource.rel('archive', False, required=False),
        'desk': Resource.rel('desks', required=False)
    }

    url = 'archive/<{0}:target_id>/link'.format(item_url)

    resource_methods = ['POST']
    item_methods = []


class ArchiveLinkService(Service):
    packageService = PackageService()

    def create(self, docs, **kwargs):
        target_id = request.view_args['target_id']
        doc = docs[0]
        link_id = doc.get('link_id')
        desk_id = doc.get('desk')
        service = get_resource_service(ARCHIVE)
        target = service.find_one(req=None, _id=target_id)
        link = {'task.desk': desk_id} if desk_id else {}
        if link_id:
            link = service.find_one(req=None, _id=link_id)

        linked_item = self.packageService.create_takes_package(target, link)
        print(linked_item)
        return [linked_item['_id']]
