# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from eve.methods.common import resolve_document_etag

from apps.common.components.base_component import BaseComponent
from apps.common.models.utils import get_model
from apps.common.components.utils import get_component
from apps.legal_archive.components.error import Error
from apps.legal_archive.models.archive_versions_model import LegalArchiveVersionsModel


class LegalArchiveVersions(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'archive_versions'

    def create(self, items):
        ids = []

        try:
            archive_versions_model = get_model(LegalArchiveVersionsModel)

            for item in items:
                item_if_exists = archive_versions_model.find_one(filter={'_id': item['_id']})
                if item_if_exists is None:
                    resolve_document_etag(item, 'archive_versions')
                    ids.extend(archive_versions_model.create([item]))
        except Exception as e:
            get_component(Error).create(LegalArchiveVersionsModel.name(), items, str(e))

        return ids
