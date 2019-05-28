# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk import get_resource_service, config
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE


def auto_publish(item, **kwargs):
    """
    Publish the passed item. The macro must be called as an on stage macro as publishing an item that is in transit
    i.e. an incoming or outgoing macro will fail.
    :param item:
    :param kwargs:
    :return:
    """
    get_resource_service('archive_publish').patch(id=item[config.ID_FIELD],
                                                  updates={ITEM_STATE: CONTENT_STATE.PUBLISHED, 'auto_publish': True})
    return item


name = 'Auto Publish'
label = 'Auto Publish'
callback = auto_publish
access_type = 'backend'
action_type = 'direct'
