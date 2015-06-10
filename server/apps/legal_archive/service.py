# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.services import BaseService


class LegalArchiveVersionsService(BaseService):
    def create(self, docs, **kwargs):
        ids = []
        for doc in docs:
            doc_if_exists = self.find_one(req=None, _id=doc['_id'])
            if doc_if_exists is None:
                ids.extend(super().create([doc]))

        return ids
