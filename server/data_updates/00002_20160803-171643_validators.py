# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : mugur
# Creation: 2016-08-03 17:16

from superdesk.commands.data_updates import BaseDataUpdate
from apps.prepopulate.app_initialize import AppInitializeWithDataCommand


class DataUpdate(BaseDataUpdate):

    resource = "validators"

    def forwards(self, mongodb_collection, mongodb_database):
        AppInitializeWithDataCommand().run(entity_name="validators")

    def backwards(self, mongodb_collection, mongodb_database):
        pass
