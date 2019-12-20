# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import json
from copy import deepcopy
from eve.utils import config, ParsedRequest
from superdesk import get_resource_service
from superdesk.errors import StopDuplication, InvalidStateTransitionError
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE, PUBLISH_SCHEDULE, SCHEDULE_SETTINGS, \
    PROCESSED_FROM, PUBLISH_STATES
from apps.archive.common import ITEM_OPERATION
from apps.publish.content.common import publish_services
from apps.content_types import apply_schema


def internal_destination_auto_publish(item, **kwargs):
    """Auto publish the item using internal destination

    :param dict item: item to be published
    :param kwargs:
    :raises StopDuplication: to indicate the superdesk.internal_destination.handle_item_published
    to stop duplication as duplication is handle by this method.
    """
    if item.get(ITEM_STATE) not in PUBLISH_STATES:
        raise InvalidStateTransitionError(message='Internal Destination auto publish macro can '
                                                  'only be called after publishing the item.')
    operation = item.get(ITEM_OPERATION)
    archive_action_service = get_resource_service(publish_services.get(operation))
    archive_service = get_resource_service('archive')
    extra_fields = [PUBLISH_SCHEDULE, SCHEDULE_SETTINGS]
    # if any macro is doing publishing then we need the duplicate item that was published earlier
    req = ParsedRequest()
    req.where = json.dumps({
        '$and': [
            {PROCESSED_FROM: item.get(config.ID_FIELD)},
            {'task.desk': str(item.get('task').get('desk'))}
        ]
    })
    req.max_results = 1
    overwrite_item = next((archive_service.get_from_mongo(req=req, lookup=None)), None)

    # keep pubslish_schedule and schedule_settings in updates so that state can be set to scheduled
    updates = {
        PUBLISH_SCHEDULE: item[PUBLISH_SCHEDULE],
        SCHEDULE_SETTINGS: item[SCHEDULE_SETTINGS]
    }
    if item.get(ITEM_STATE) == CONTENT_STATE.PUBLISHED or not overwrite_item:
        new_id = archive_service.duplicate_content(item, state='routed', extra_fields=extra_fields)
        updates[ITEM_STATE] = item.get(ITEM_STATE)
        updates[PROCESSED_FROM] = item[config.ID_FIELD]

        get_resource_service('archive_publish').patch(id=new_id, updates=updates)
    else:
        if overwrite_item:
            # get the schema fields
            schema_item = apply_schema(deepcopy(item))
            keys_to_delete = ['source', 'unique_id', 'unique_name', 'original_id',
                              'expiry', 'correction_sequence']
            # remove the keys
            archive_service.remove_after_copy(schema_item, delete_keys=keys_to_delete)
            # get the diff
            updates.update({key: val for key, val in schema_item.items()
                            if overwrite_item.get(key) != val and not key.startswith("_")})

            archive_action_service.patch(id=overwrite_item[config.ID_FIELD],
                                         updates=updates)

    # raise stop duplication on successful completion so that
    # internal destination superdesk.internal_destination.handle_item_published
    # will not duplicate the item.
    raise StopDuplication()


name = 'Internal_Destination_Auto_Publish'
label = 'Internal Destination Auto Publish'
callback = internal_destination_auto_publish
access_type = 'backend'
action_type = 'direct'
