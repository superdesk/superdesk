# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
import logging
import superdesk

from superdesk.utc import utcnow
from superdesk.errors import SubscriberError, SuperdeskPublishError, PublishQueueError


logger = logging.getLogger(__name__)


class PublishService():
    """Base publish service class."""

    def _transmit(self, item, subscriber, destination):
        raise NotImplementedError()

    def transmit(self, item, subscriber, destination):
        if not subscriber.get('is_active'):
            raise SubscriberError.subscriber_inactive_error(Exception('Subscriber inactive'), subscriber)
        else:
            try:
                self._transmit(item, subscriber, destination) or []
                update_item_status(item, 'success')
            except SuperdeskPublishError as error:
                update_item_status(item, 'error', error)
                raise error


def update_item_status(item, status, error=None):
    try:
        item_update = {'state': status}
        if status == 'in-progress':
            item_update['transmit_started_at'] = utcnow()
        elif status == 'success':
            item_update['completed_at'] = utcnow()
        elif status == 'error' and error:
            item_update['error_message'] = str(error)

        superdesk.get_resource_service('publish_queue').patch(item.get('_id'), item_update)
    except Exception as ex:
        raise PublishQueueError.item_update_error(ex)


def get_file_extension(item):
    try:
        format = item['format'].upper()
        if format == 'NITF':
            return 'ntf'
        if format == 'XML':
            return 'xml'
    except Exception as ex:
        raise PublishQueueError.item_update_error(ex)
