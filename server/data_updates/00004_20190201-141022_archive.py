# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Creation: 2018-11-14 10:31

from superdesk.commands.data_updates import DataUpdate
from superdesk import get_resource_service
from superdesk.metadata.item import CONTENT_STATE, \
    CONTENT_TYPE, ITEM_STATE, ITEM_TYPE
from eve.utils import ParsedRequest


class DataUpdate(DataUpdate):

    resource = 'archive'

    def forwards(self, mongodb_collection, mongodb_database):
        archive_service = get_resource_service('archive')

        req = ParsedRequest()
        req.max_results = 50
        lookup = {
            ITEM_STATE: CONTENT_STATE.DRAFT,
            ITEM_TYPE: CONTENT_TYPE.PICTURE
        }
        while True:
            items = list(archive_service.get(req=req, lookup=lookup))
            if not items:
                break
            for item in items:
                archive_service.system_update(
                    item['_id'], {ITEM_STATE: CONTENT_STATE.PROGRESS}, item
                )

    def backwards(self, mongodb_collection, mongodb_database):
        pass
