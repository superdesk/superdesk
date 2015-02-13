# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from apps.common.components.base_component import BaseComponent
from apps.common.models.utils import get_model
from apps.legal_archive.models.legal_archive import LegalArchiveModel
from apps.common.components.utils import get_component
from apps.legal_archive.components.error import Error
from copy import copy, deepcopy


class LegalArchive(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'legal_archive'

    def create(self, items):
        citems = deepcopy(items)
        for citem in citems:
            citem['_id_document'] = citem['_id']
            del citem['_id']
        try:
            return get_model(LegalArchiveModel).create(citems)
        except Exception as e:
            get_component(Error).create(LegalArchiveModel.name(), items, str(e))

    def update(self, original, updates):
        updated = copy(original)
        updated.update(updates)
        updated['_id_document'] = original['_id']
        del updated['_id']
        try:
            return get_model(LegalArchiveModel).create([updated])
        except Exception as e:
            get_component(Error).create(LegalArchiveModel.name(), [updated], str(e))
