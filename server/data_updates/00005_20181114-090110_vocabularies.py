# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Creation: 2018-11-14 10:31

from superdesk.commands.data_updates import BaseDataUpdate
from superdesk import get_resource_service


class DataUpdate(BaseDataUpdate):

    resource = "vocabularies"

    def forwards(self, mongodb_collection, mongodb_database):
        vocabularies_service = get_resource_service("vocabularies")
        for vocabulary in vocabularies_service.get(req=None, lookup=None):
            if vocabulary.get("selection_type"):
                continue
            if vocabulary.get("single_value", False):
                value = "single selection"
            else:
                value = "multi selection"
            mongodb_collection.update(
                {"_id": vocabulary["_id"]}, {"$set": {"selection_type": value}, "$unset": {"single_value": 1}}
            )

    def backwards(self, mongodb_collection, mongodb_database):
        vocabularies_service = get_resource_service("vocabularies")
        for vocabulary in vocabularies_service.get(req=None, lookup=None):
            if vocabulary.get("selection_type") == "single selection":
                value = True
            else:
                value = False
            mongodb_collection.update(
                {"_id": vocabulary["_id"]}, {"$set": {"single_value": value}, "$unset": {"selection_type": 1}}
            )
