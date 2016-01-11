# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from eve.utils import config
from flask import request

from superdesk import get_resource_service, Service
from superdesk.metadata.item import EMBARGO
from superdesk.resource import Resource, build_custom_hateoas
from apps.packages import TakesPackageService
from apps.archive.common import CUSTOM_HATEOAS, BROADCAST_GENRE, is_genre, insert_into_versions
from apps.auth import get_user
from superdesk.metadata.utils import item_url
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
        link = {}

        if desk_id:
            link = {'task': {'desk': desk_id}}
            user = get_user()
            lookup = {'_id': desk_id, 'members.user': user['_id']}
            desk = get_resource_service('desks').find_one(req=None, **lookup)
            if not desk:
                raise SuperdeskApiError.forbiddenError("No privileges to create new take on requested desk.")

            link['task']['stage'] = desk['working_stage']

        if link_id:
            link = service.find_one(req=None, _id=link_id)

        linked_item = self.packageService.link_as_next_take(target, link)
        insert_into_versions(id_=linked_item[config.ID_FIELD])
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

        if target.get(EMBARGO):
            raise SuperdeskApiError.badRequestError("Takes can't be created for an Item having Embargo")

        if is_genre(target, BROADCAST_GENRE):
            raise SuperdeskApiError.badRequestError("Cannot add new take to the story with genre as broadcast.")

        if get_resource_service('published').is_rewritten_before(target['_id']):
            raise SuperdeskApiError.badRequestError(message='Article has been rewritten before !')
