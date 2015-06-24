# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging

from flask import g

from superdesk import Service, get_resource_privileges
from superdesk.errors import SuperdeskApiError

logger = logging.getLogger(__name__)


class LegalService(Service):

    def get(self, req, lookup):
        self.check_get_access_privilege()
        return super().get(req, lookup)

    def check_get_access_privilege(self):
        if not hasattr(g, 'user'):
            return

        privileges = g.user.get('active_privileges', {})
        resource_privileges = get_resource_privileges(self.datasource).get('GET', None)
        if privileges.get(resource_privileges, 0) == 0:
            raise SuperdeskApiError.forbiddenError()


class LegalArchiveService(LegalService):
    pass


class LegalPublishQueueService(LegalService):
    pass


class LegalArchiveVersionsService(LegalService):
    def create(self, docs, **kwargs):
        ids = []
        for doc in docs:
            doc_if_exists = self.find_one(req=None, _id=doc['_id'])
            if doc_if_exists is None:
                ids.extend(super().create([doc]))

        return ids
