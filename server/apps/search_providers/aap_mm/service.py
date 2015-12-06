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

from eve.utils import config
from flask import json

import superdesk
from apps.archive.archive import SOURCE as ARCHIVE
from apps.archive.common import generate_unique_id_and_name
from apps.archive.common import insert_into_versions, remove_unwanted, set_original_creator
from apps.tasks import send_to
from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError, ProviderError
from superdesk.metadata.item import GUID_TAG, FAMILY_ID, INGEST_ID, ITEM_STATE, CONTENT_STATE
from superdesk.metadata.utils import generate_guid
from apps.search_providers.aap_mm import PROVIDER_NAME
from superdesk.utc import utcnow

logger = logging.getLogger(__name__)


class AAPMMService(superdesk.Service):

    def create(self, docs, **kwargs):
        search_provider = get_resource_service('search_providers').find_one(search_provider=PROVIDER_NAME, req=None)

        if not search_provider or search_provider.get('is_closed', False):
            raise SuperdeskApiError.badRequestError('No search provider found or the search provider is closed.')

        if 'config' in search_provider:
            self.backend.set_credentials(search_provider['config'])

        new_guids = []
        for doc in docs:
            if not doc.get('desk'):  # if no desk is selected then it is bad request
                raise SuperdeskApiError.badRequestError("Destination desk cannot be empty.")

            try:
                archived_doc = self.backend.find_one_raw(doc['guid'], doc['guid'])
            except FileNotFoundError as ex:
                raise ProviderError.externalProviderError(ex, search_provider)

            dest_doc = dict(archived_doc)
            new_id = generate_guid(type=GUID_TAG)
            new_guids.append(new_id)
            dest_doc[config.ID_FIELD] = new_id
            generate_unique_id_and_name(dest_doc)

            if search_provider:
                dest_doc['ingest_provider'] = str(search_provider[config.ID_FIELD])

            dest_doc[config.VERSION] = 1
            send_to(doc=dest_doc, update=None, desk_id=doc.get('desk'), stage_id=doc.get('stage'))
            dest_doc[ITEM_STATE] = doc.get(ITEM_STATE, CONTENT_STATE.FETCHED)
            dest_doc[INGEST_ID] = archived_doc[config.ID_FIELD]
            dest_doc[FAMILY_ID] = archived_doc[config.ID_FIELD]
            remove_unwanted(dest_doc)
            set_original_creator(dest_doc)

            superdesk.get_resource_service(ARCHIVE).post([dest_doc])
            insert_into_versions(dest_doc[config.ID_FIELD])

            get_resource_service('search_providers').system_update(search_provider[config.ID_FIELD],
                                                                   {'last_item_update': utcnow()}, search_provider)

        return new_guids

    def get(self, req, lookup):
        search_provider = get_resource_service('search_providers').find_one(search_provider=PROVIDER_NAME, req=None)

        if not search_provider or search_provider.get('is_closed', False):
            raise SuperdeskApiError.badRequestError('No search provider found or the search provider is closed.')

        if search_provider:
            if 'config' in search_provider:
                self.backend.set_credentials(search_provider['config'])

            query = self._get_query(req)
            results = self.backend.find(PROVIDER_NAME, query, None)

            for doc in results.docs:
                doc['ingest_provider'] = str(search_provider[config.ID_FIELD])

            return results

    def _get_query(self, req):
        args = getattr(req, 'args', {})
        query = json.loads(args.get('source')) if args.get('source') else {'query': {'filtered': {}}}

        return query
