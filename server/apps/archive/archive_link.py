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

from superdesk import get_resource_service, Service
from superdesk.resource import Resource, build_custom_hateoas
from apps.packages import TakesPackageService
from apps.archive.common import item_url, CUSTOM_HATEOAS
from apps.archive.archive import SOURCE as ARCHIVE
from superdesk.errors import SuperdeskApiError
import logging

logger = logging.getLogger(__name__)


class ArchiveLinkResource(Resource):
    endpoint_name = 'archive_link'
    resource_title = endpoint_name

    schema = {
        'link_id': Resource.rel('archive', embeddable=False, type='string'),
        'desk': Resource.rel('desks', embeddable=False)
    }

    url = 'archive/<{0}:target_id>/link'.format(item_url)

    resource_methods = ['POST']
    item_methods = []


class ArchiveLinkService(Service):
    packageService = TakesPackageService()

    def create(self, docs, **kwargs):
        target_id = request.view_args['target_id']
        doc = docs[0]
        link_id = doc.get('link_id')
        desk_id = doc.get('desk')
        service = get_resource_service(ARCHIVE)
        target = service.find_one(req=None, _id=target_id)
        self._validate_link(target, target_id)

        link = {'task': {'desk': desk_id}} if desk_id else {}

        if link_id:
            link = service.find_one(req=None, _id=link_id)

        linked_item = self.packageService.link_as_next_take(target, link)
        doc.update(linked_item)
        build_custom_hateoas(CUSTOM_HATEOAS, doc)
        return [linked_item['_id']]

    def _validate_link(self, target, target_id):
        """
        Validates the article to be linked
        :param target: article to be linked
        :param target_id: id of the article to be linked
        :raises: SuperdeskApiError
        """
        if not target:
            raise SuperdeskApiError.notFoundError(message='Cannot find the target item with id {}.'.format(target_id))

        if get_resource_service('published').is_rewritten_before(target['_id']):
            raise SuperdeskApiError.badRequestError(message='Article has been rewritten before !')
