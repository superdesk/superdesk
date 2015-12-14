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
from superdesk import get_resource_service
from superdesk.utc import utcnow

from eve.utils import config, ParsedRequest

from apps.archive.common import ITEM_OPERATION
# from apps.publish.content.common import ITEM_PUBLISH, ITEM_CORRECT, ITEM_KILL
from apps.publish.enqueue.enqueue_corrected import EnqueueCorrectedService
from apps.publish.enqueue.enqueue_killed import EnqueueKilledService
from apps.publish.enqueue.enqueue_published import EnqueuePublishedService
from apps.publish.published_item import QUEUE_STATE, PUBLISH_STATE, PUBLISHED


logger = logging.getLogger(__name__)


ITEM_PUBLISH = 'publish'
ITEM_CORRECT = 'correct'
ITEM_KILL = 'kill'


enqueue_services = {
    ITEM_PUBLISH: EnqueuePublishedService(),
    ITEM_CORRECT: EnqueueCorrectedService(),
    ITEM_KILL: EnqueueKilledService()
}


def get_enqueue_service(operation):
    return enqueue_services[operation]


def enqueue_item(published_item):
    """
    Creates the corresponding entries in the publish queue for the given item
    """
    published_item_id = published_item[config.ID_FIELD]
    published_service = get_resource_service(PUBLISHED)
    published_update = {QUEUE_STATE: PUBLISH_STATE.IN_PROGRESS, 'last_queue_event': utcnow()}
    published_service.patch(published_item_id, published_update)
    try:
        get_enqueue_service(published_item[ITEM_OPERATION]).enqueue_item(published_item)
        published_service.patch(published_item_id, {QUEUE_STATE: PUBLISH_STATE.QUEUED})
    except KeyError:
        published_service.patch(published_item_id, {QUEUE_STATE: PUBLISH_STATE.PENDING})
        logger.error('No enqueue service found for operation %s', published_item[ITEM_OPERATION])
    except:
        published_service.patch(published_item_id, {QUEUE_STATE: PUBLISH_STATE.PENDING})
        raise
