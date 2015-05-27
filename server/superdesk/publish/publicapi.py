# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import json

from apps.content import ITEM_TYPE_COMPOSITE
from superdesk import get_resource_service
from superdesk.errors import PublishPublicAPIError
from superdesk.publish import register_transmitter
from superdesk.publish.publish_service import PublishService


errors = [PublishPublicAPIError.publicAPIError().get_error_description()]


class PublicAPIPublishService(PublishService):
    """Public API Publish Service."""

    def _transmit(self, formatted_item, subscriber, destination):
        item = json.loads(formatted_item['formatted_item'])
        if item['type'] == ITEM_TYPE_COMPOSITE:
            publicapiService = get_resource_service('public_packages')
        else:
            publicapiService = get_resource_service('public_items')
        try:
            public_item = publicapiService.find_one(req=None, _id=item['_id'])
            if public_item:
                publicapiService.patch(item['_id'], item)
            else:
                publicapiService.post([item])
        except Exception as ex:
            raise PublishPublicAPIError.publicAPIError(ex, destination)

register_transmitter('publicapi', PublicAPIPublishService(), errors)
