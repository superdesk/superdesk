# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : petr
# Creation: 2016-08-29 09:41

from superdesk.commands.data_updates import DataUpdate


class DataUpdate(DataUpdate):

    resource = 'validators'

    def forwards(self, mongodb_collection, mongodb_database):
        mongodb_collection.update_many(
            {'_id': {'$in': ['publish_embedded_picture', 'correct_embedded_picture']}},
            {'$set': {'embedded': True}}
        )

    def backwards(self, mongodb_collection, mongodb_database):
        pass
