# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from superdesk.errors import SuperdeskApiError
from superdesk.metadata.item import CONTENT_TYPE, ITEM_TYPE, ITEM_STATE, CONTENT_STATE

from apps.archive.common import set_sign_off, ITEM_OPERATION

from .common import BasePublishService, BasePublishResource, ITEM_PUBLISH


logger = logging.getLogger(__name__)


class ArchivePublishResource(BasePublishResource):
    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'publish')


class ArchivePublishService(BasePublishService):
    publish_type = 'publish'
    published_state = 'published'

    def _validate(self, original, updates):
        super()._validate(original, updates)
        if original[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
            items = self.package_service.get_residrefs(original)

            if len(items) == 0 and self.publish_type == ITEM_PUBLISH:
                raise SuperdeskApiError.badRequestError("Empty package cannot be published!")

    def on_update(self, updates, original):
        updates[ITEM_OPERATION] = ITEM_PUBLISH
        super().on_update(updates, original)
        set_sign_off(updates, original)

    def set_state(self, original, updates):
        """
        Set the state of the document to schedule if the publish_schedule is specified.
        :param dict original: original document
        :param dict updates: updates related to original document
        """

        updates.setdefault(ITEM_OPERATION, ITEM_PUBLISH)
        if original.get('publish_schedule') or updates.get('publish_schedule'):
            updates[ITEM_STATE] = CONTENT_STATE.SCHEDULED
        else:
            super().set_state(original, updates)
