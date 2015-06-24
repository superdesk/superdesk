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

from apps.content import ITEM_TYPE, ITEM_TYPE_COMPOSITE
from superdesk import get_resource_service
from superdesk.errors import PublishPublicAPIError
from superdesk.publish import register_transmitter
from superdesk.publish.publish_service import PublishService
from datetime import datetime


errors = [PublishPublicAPIError.publicAPIError().get_error_description()]


class PublicAPIPublishService(PublishService):
    """Public API Publish Service."""

    def _transmit(self, queue_item, subscriber):
        config = queue_item.get('destination', {}).get('config', {})

        item = json.loads(queue_item['formatted_item'])
        self._fix_dates(item)

        if item[ITEM_TYPE] == ITEM_TYPE_COMPOSITE:
            public_api_service = get_resource_service('publish_packages')
        else:
            public_api_service = get_resource_service('publish_items')

        try:
            public_item = public_api_service.find_one(req=None, _id=item['_id'])

            if public_item:
                public_api_service.patch(item['_id'], item)
            else:
                public_api_service.post([item])
        except Exception as ex:
            raise PublishPublicAPIError.publicAPIError(ex, config)

    def _fix_dates(self, item):
        for field, value in item.items():
            if isinstance(value, dict) and '$date' in value:
                item[field] = datetime.utcfromtimestamp(value['$date'] / 1000)

register_transmitter('PublicArchive', PublicAPIPublishService(), errors)
