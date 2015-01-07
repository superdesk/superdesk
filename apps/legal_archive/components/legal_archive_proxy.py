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
from apps.legal_archive.tasks import update_legal_archive


class LegalArchiveProxy(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'legal_archive_proxy'

    def create(self, items):
        return update_legal_archive.delay([item['_id'] for item in items])

    def update(self, original, updates):
        return update_legal_archive.delay([original['_id']])
