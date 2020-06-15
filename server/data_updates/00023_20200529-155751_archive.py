# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : petr
# Creation: 2020-05-29 15:57

import re
import logging

from superdesk.commands.data_updates import DataUpdate
from superdesk import get_resource_service

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DataUpdate(DataUpdate):

    resource = 'archive'

    def forwards(self, mongodb_collection, mongodb_database):
        service = get_resource_service(self.resource)
        desk = mongodb_database['desks'].find_one({'name': re.compile(r'^XFV')})  # image desk
        if not desk:
            logger.warning('desk XFV not found')
            return
        ids = list(mongodb_collection.find({'state': 'published', 'task.desk': None}, {'_id': True}))
        if ids:
            logger.info('attaching %d items to desk %s', len(ids), desk['name'])
        else:
            logger.info('no published items without desk found')
        for _id in ids:
            item = service.find_one(req=None, _id=_id['_id'])
            updates = {
                'task': {
                    'desk': desk['_id'],
                    'stage': desk['working_stage'],
                    'user': item.get('original_creator'),
                },
            }
            logger.info('updating item %s', item['_id'])
            service.system_update(item['_id'], updates, item)

    def backwards(self, mongodb_collection, mongodb_database):
        pass
