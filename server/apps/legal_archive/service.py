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
from eve.versioning import versioned_id_field

from flask import g

from eve.utils import config, ParsedRequest
from .resource import LEGAL_ARCHIVE_NAME

from superdesk import Service, get_resource_privileges
from superdesk.errors import SuperdeskApiError
from superdesk.utils import ListCursor

logger = logging.getLogger(__name__)


class LegalService(Service):

    def get(self, req, lookup):
        self.check_get_access_privilege()
        return super().get(req, lookup)

    def find_one(self, req, **lookup):
        self.check_get_access_privilege()
        return super().find_one(req, **lookup)

    def check_get_access_privilege(self):
        if not hasattr(g, 'user'):
            return

        privileges = g.user.get('active_privileges', {})
        resource_privileges = get_resource_privileges(self.datasource).get('GET', None)
        if privileges.get(resource_privileges, 0) == 0:
            raise SuperdeskApiError.forbiddenError()

    def enhance(self, legal_archive_docs):
        """
        Enhances the item in Legal Archive Service
        :param legal_archive_docs:
        """

        if isinstance(legal_archive_docs, list):
            for legal_archive_doc in legal_archive_docs:
                legal_archive_doc['_type'] = LEGAL_ARCHIVE_NAME
        else:
            legal_archive_docs['_type'] = LEGAL_ARCHIVE_NAME


class LegalArchiveService(LegalService):
    def on_fetched(self, docs):
        """
        Overriding this to enhance the published article with the one in archive collection
        """

        self.enhance(docs[config.ITEMS])

    def on_fetched_item(self, doc):
        """
        Overriding this to enhance the published article with the one in archive collection
        """

        self.enhance(doc)


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

    def get(self, req, lookup):
        """
        Version of an article in Legal Archive isn't maintained by Eve. Overriding this to fetch the version history.
        """

        id_field = versioned_id_field({'id_field': config.ID_FIELD})

        if req and req.args and req.args.get(config.ID_FIELD):
            version_history = list(super().get_from_mongo(req=ParsedRequest(),
                                                          lookup={id_field: req.args.get(config.ID_FIELD)}))
        else:
            version_history = list(super().get_from_mongo(req=req, lookup=lookup))

        for doc in version_history:
            doc[config.ID_FIELD] = doc[id_field]
            del doc[id_field]
            self.enhance(doc)

        return ListCursor(version_history)
