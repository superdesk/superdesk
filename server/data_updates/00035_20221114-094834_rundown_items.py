# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : petr
# Creation: 2022-11-14 09:48

from superdesk.commands.data_updates import BaseDataUpdate


class DataUpdate(BaseDataUpdate):

    resource = 'rundown_items'

    def forwards(self, mongodb_collection, mongodb_database):
        res = mongodb_collection.update_many({"subitems": {"$exists": 1}}, {"$unset": {"subitems": 1}})
        print("updated {}".format(res.modified_count))

    def backwards(self, mongodb_collection, mongodb_database):
        pass
