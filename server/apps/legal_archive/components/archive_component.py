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
from apps.legal_archive.models.archive_model import LegalArchiveModel
from apps.common.components.utils import get_component
from apps.legal_archive.components.error import Error


class LegalArchive(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'archive'

    def find_one(self, filter, projection=None):
        try:
            return get_model(LegalArchiveModel).find_one(filter, projection)
        except Exception as e:
            get_component(Error).create(LegalArchiveModel.name(), filter, str(e))

    def create(self, items):
        try:
            return get_model(LegalArchiveModel).create(items)
        except Exception as e:
            get_component(Error).create(LegalArchiveModel.name(), items, str(e))

    def replace(self, filter, doc, etag=None):
        try:
            return get_model(LegalArchiveModel).replace(filter, doc, etag=None)
        except Exception as e:
            get_component(Error).create(LegalArchiveModel.name(), doc, str(e))
