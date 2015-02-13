# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from apps.common.models.base_model import BaseModel
from apps.item_lock.models.item import ItemValidator


class ItemAutosaveModel(BaseModel):
    def __init__(self, data_layer):
        BaseModel.__init__(self, 'archive_autosave', data_layer, {}, ItemValidator())

    @classmethod
    def name(cls):
        return 'item_autosave'
