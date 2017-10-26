# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : mugur
# Creation: 2017-10-26 10:31

from superdesk.commands.data_updates import DataUpdate
from superdesk import get_resource_service


class DataUpdate(DataUpdate):

    resource = 'content_types'

    def forwards(self, mongodb_collection, mongodb_database):
        content_types_service = get_resource_service('content_types')
        for content_type in content_types_service.get(req=None, lookup=None):
            content_types_service.patch(content_type['_id'], {})

    def backwards(self, mongodb_collection, mongodb_database):
        pass
