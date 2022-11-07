# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : petr
# Creation: 2022-11-07 16:15

from superdesk.commands.data_updates import BaseDataUpdate


class DataUpdate(BaseDataUpdate):

    resource = "rundown_items"

    def forwards(self, mongodb_collection, mongodb_database):
        updated = 0
        for rundown in mongodb_database["rundowns"].find():
            if rundown.get("items"):
                updated += mongodb_collection.update_many(
                    {"_id": {"$in": [item["_id"] for item in rundown["items"]]}},
                    {"$set": {"rundown": rundown["_id"]}},
                ).modified_count
        print("updated {updated} items".format(updated=updated))

    def backwards(self, mongodb_collection, mongodb_database):
        print(
            "reverted {} items".format(
                mongodb_collection.update_many({"rundown": {"$exists": 1}}, {"$unset": {"rundown": 1}}).modified_count
            )
        )
