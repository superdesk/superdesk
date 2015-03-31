# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from eve.io.mongo import Mongo
from eve.io.base import ConnectionException


class LegalArchiveDataLayer(Mongo):
    """Superdesk Data Layer"""

    def init_app(self, app):
        try:
            super().init_app(app)
        except Exception as e:
            raise ConnectionException(e)

    def current_mongo_prefix(self):
        return self.app.config['LEGAL_ARCHIVE_DBNAME']

    def delete(self, resource, lookup):
        self.remove(resource, lookup)

    def create(self, resource, docs, **kwargs):
        self.insert(resource, docs)
