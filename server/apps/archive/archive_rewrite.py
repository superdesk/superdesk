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
from apps.archive.common import item_url, CUSTOM_HATEOAS
from superdesk.workflow import is_workflow_state_transition_valid
from superdesk.errors import SuperdeskApiError, InvalidStateTransitionError
from apps.packages.takes_package_service import TakesPackageService
from apps.tasks import send_to
from eve.utils import config
import logging

logger = logging.getLogger(__name__)


class ArchiveRewriteResource(Resource):
    endpoint_name = 'archive_rewrite'
    resource_title = endpoint_name

    schema = {
        'desk_id': {"type": "string"}
    }

    url = 'archive/<{0}:original_id>/rewrite'.format(item_url)
    resource_methods = ['POST']
    privileges = {'POST': 'rewrite'}


class ArchiveRewriteService(Service):
    def create(self, docs, **kwargs):
        original_id = request.view_args['original_id']
        archive_service = get_resource_service('archive')
        original = archive_service.find_one(req=None, _id=original_id)
        self._validate_rewrite(original)
        digital = TakesPackageService().get_take_package(original)
        rewrite = self._create_rewrite_article(original, digital)
        archive_service.post([rewrite])
        build_custom_hateoas(CUSTOM_HATEOAS, rewrite)
        self._add_rewritten_flag(original, digital, rewrite)
        return [rewrite]

    def _validate_rewrite(self, original):
        """
        Validates the article to be rewritten
        :param original: article to be rewritten
        :raises: SuperdeskApiError
        """
        if not original:
            raise SuperdeskApiError.notFoundError(message='Cannot find the article')

        if not original.get('event_id'):
            raise SuperdeskApiError.notFoundError(message='Event id does not exist')

        if get_resource_service('published').is_rewritten_before(original['_id']):
            raise SuperdeskApiError.badRequestError(message='Article has been rewritten before !')

        if not is_workflow_state_transition_valid('rewrite', original[config.CONTENT_STATE]):
            raise InvalidStateTransitionError()

        if not TakesPackageService().is_last_takes_package_item(original):
            raise SuperdeskApiError.badRequestError(message="Only last take of the package can be rewritten.")

    def _create_rewrite_article(self, original, digital):
        """
        Creates a new story and sets the metadata from original and digital
        :param original: original story
        :param digital: digital version of the story
        :return:new story
        """
        rewrite = dict()
        fields = ['family_id', 'abstract', 'anpa_category', 'pubstatus', 'slugline', 'urgency', 'subject', 'priority',
                  'byline', 'dateline', 'headline', 'event_id']

        for field in fields:
            if original.get(field):
                rewrite[field] = original[field]

        if digital:
            # check if there's digital
            rewrite['rewrite_of'] = digital['_id']
        else:
            # if not use original's id
            rewrite['rewrite_of'] = original['_id']

        send_to(doc=rewrite, desk_id=original['task']['desk'])
        rewrite['state'] = 'in_progress'
        self._set_take_key(rewrite, original.get('event_id'))
        return rewrite

    def _add_rewritten_flag(self, original, digital, rewrite):
        """ Adds rewritten_by field to the existing published items """
        get_resource_service('published').update_published_items(original['_id'], 'rewritten_by', rewrite['_id'])
        if digital:
            get_resource_service('published').update_published_items(digital['_id'], 'rewritten_by', rewrite['_id'])

    def _clear_rewritten_flag(self, event_id, rewrite_id):
        """ Clears rewritten_by field from the existing published items """
        publish_service = get_resource_service('published')
        published_rewritten_stories = publish_service.get_rewritten_items_by_event_story(event_id, rewrite_id)
        for doc in published_rewritten_stories:
            get_resource_service('published').update_published_items(doc['item_id'], 'rewritten_by', None)

    def _set_take_key(self, rewrite, event_id):
        """
        Sets the anpa take key of the rewrite with ordinal
        :param rewrite: rewrite story
        :param event_id: event id
        """
        published_digital_stories = get_resource_service('published'). \
            get_rewritten_take_packages_per_event(event_id)

        digital_count = published_digital_stories.count()
        if digital_count > 0:
            ordinal = self._get_ordinal(digital_count + 1)
            rewrite['anpa_take_key'] = '{} update'.format(ordinal)
        else:
            rewrite['anpa_take_key'] = 'update'

    def _get_ordinal(self, n):
        """ Returns the ordinal value of the given int """
        if 10 <= n % 100 < 20:
            return str(n) + 'th'
        else:
            return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, "th")
