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

from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE
from superdesk import get_resource_service, config, app
from superdesk.errors import PublishPublicAPIError
from superdesk.publish import register_transmitter
from superdesk.publish.publish_service import PublishService
from datetime import datetime
from io import BytesIO
from bson import ObjectId


errors = [PublishPublicAPIError.publicAPIError().get_error_description()]


class PublicAPIPublishService(PublishService):
    """Public API Publish Service."""

    def _transmit(self, queue_item, subscriber):
        config = queue_item.get('destination', {}).get('config', {})

        try:
            item = json.loads(queue_item['formatted_item'])
            self._fix_dates(item)
            self._copy_published_media_files(item)

            if item[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
                public_api_service = get_resource_service('publish_packages')
            else:
                public_api_service = get_resource_service('publish_items')

            public_item = public_api_service.find_one(req=None, _id=item['_id'])

            if public_item:
                public_api_service.patch(item['_id'], item)
            else:
                public_api_service.post([item])
        except Exception as ex:
            raise PublishPublicAPIError.publicAPIError(ex, config)

    def _fix_dates(self, item):
        for field, value in item.items():
            if isinstance(value, str):
                try:
                    new_value = datetime.strptime(value, config.DATE_FORMAT)
                    item[field] = new_value
                except:
                    pass

    def _copy_published_media_files(self, item):
        for k, v in item.get('renditions', {}).items():
            if k == 'original_source':
                # if the source is AAP Multimedia then don't copy
                continue

            del v['href']
            if not app.media.exists(v['media'], resource='publish_items'):
                img = app.media.get(v['media'], resource='upload')
                content = BytesIO(img.read())
                content.seek(0)
                _id = app.media.put(content, filename=img.filename, content_type=img.content_type,
                                    metadata=img.metadata, resource='publish_items', _id=ObjectId(v['media']))
                assert str(_id) == v['media']


register_transmitter('PublicArchive', PublicAPIPublishService(), errors)
