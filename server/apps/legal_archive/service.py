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
from flask import g, current_app as app
from eve.utils import config, ParsedRequest
from .resource import LEGAL_ARCHIVE_NAME
from superdesk import Service, get_resource_privileges
from superdesk.errors import SuperdeskApiError
from superdesk.metadata.item import ITEM_TYPE, GUID_FIELD, CONTENT_TYPE
from superdesk.metadata.packages import GROUPS, RESIDREF, REFS
from superdesk.utils import ListCursor

logger = logging.getLogger(__name__)


class LegalService(Service):
    """
    Base Service Class for Legal Archive related services
    """

    def on_create(self, docs):
        """
        Overriding to replace the location of each item in the package to legal archive instead of archive,
        if doc is a package.
        """

        super().on_create(docs)
        for doc in docs:
            if ITEM_TYPE in doc:
                doc.setdefault(config.ID_FIELD, doc[GUID_FIELD])
                if doc[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
                    self._change_location_of_items_in_package(doc)

    def on_replace(self, document, original):
        """
        Overriding to replace the location of each item in the package to legal archive instead of archive,
        if doc is a package.
        """

        super().on_replace(document, original)
        if document.get(ITEM_TYPE) == CONTENT_TYPE.COMPOSITE:
            self._change_location_of_items_in_package(document)

    def get(self, req, lookup):
        """
        Overriding to check if user is authorized to perform get operation on Legal Archive resources. If authorized
        then request is forwarded otherwise throws forbidden error.

        :return: list of docs matching query in req and lookup
        :raises: SuperdeskApiError.forbiddenError() if user is unauthorized to access the Legal Archive resources.
        """

        self.check_get_access_privilege()
        return super().get(req, lookup)

    def find_one(self, req, **lookup):
        """
        Overriding to check if user is authorized to perform get operation on Legal Archive resources. If authorized
        then request is forwarded otherwise throws forbidden error.

        :return: doc if there is one matching the query in req and lookup
        :raises: SuperdeskApiError.forbiddenError() if user is unauthorized to access the Legal Archive resources.
        """

        self.check_get_access_privilege()
        return super().find_one(req, **lookup)

    def check_get_access_privilege(self):
        """
        Checks if user is authorized to perform get operation on Legal Archive resources. If authorized then request is
        forwarded otherwise throws forbidden error.

        :raises: SuperdeskApiError.forbiddenError() if user is unauthorized to access the Legal Archive resources.
        """

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

    def _change_location_of_items_in_package(self, package):
        """
        Changes location of each item in the package to legal archive instead of archive.
        """

        for group in package.get(GROUPS, []):
            for ref in group.get(REFS, []):
                if RESIDREF in ref:
                    ref['location'] = LEGAL_ARCHIVE_NAME


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
    def create(self, docs, **kwargs):
        """
        Overriding this from preventing the transmission details again. This happens when an item in a package expires
        at later point of time. In this case, the call to insert transmission details happens twice once when the
        package expires and once when the item expires.
        """

        ids = []
        for doc in docs:
            doc_if_exists = None
            if doc.get(config.ID_FIELD):
                doc_if_exists = self.find_one(req=None, _id=doc.get(config.ID_FIELD))
            if doc_if_exists is None:
                ids.extend(super().create([doc]))

        return ids


class LegalArchiveVersionsService(LegalService):
    def create(self, docs, **kwargs):
        """
        Overriding this from preventing the same version again. This happens when an item is published more than once.
        """

        ids = []
        for doc in docs:
            doc_if_exists = None

            if config.ID_FIELD in doc:  # This happens when inserting docs from pre-populate command
                doc_if_exists = self.find_one(req=None, _id=doc['_id'])

            if doc_if_exists is None:
                ids.extend(super().create([doc]))

        return ids

    def get(self, req, lookup):
        """
        Version of an article in Legal Archive isn't maintained by Eve. Overriding this to fetch the version history.
        """

        resource_def = app.config['DOMAIN'][LEGAL_ARCHIVE_NAME]
        id_field = versioned_id_field(resource_def)

        if req and req.args and req.args.get(config.ID_FIELD):
            version_history = list(super().get_from_mongo(req=ParsedRequest(),
                                                          lookup={id_field: req.args.get(config.ID_FIELD)}))
        else:
            version_history = list(super().get_from_mongo(req=req, lookup=lookup))

        for doc in version_history:
            doc[config.ID_FIELD] = doc[id_field]
            self.enhance(doc)

        return ListCursor(version_history)
