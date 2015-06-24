# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import superdesk
import logging
from eve.utils import config
from flask import json
from superdesk.errors import SuperdeskApiError, ProviderError
from apps.archive.common import generate_guid, generate_unique_id_and_name, GUID_TAG, FAMILY_ID, INGEST_ID
from apps.archive.common import insert_into_versions, remove_unwanted, set_original_creator
from apps.tasks import send_to
from apps.archive.archive import SOURCE as ARCHIVE
from superdesk import get_resource_service

logger = logging.getLogger(__name__)

STATE_FETCHED = 'fetched'


class AapMMService(superdesk.Service):

    def create(self, docs, **kwargs):
        new_guids = []
        provider = get_resource_service('ingest_providers').find_one(source='aapmm', req=None)
        if provider and 'config' in provider and 'username' in provider['config']:
                self.backend.set_credentials(provider['config']['username'], provider['config']['password'])
        for doc in docs:
            if not doc.get('desk'):
                # if no desk is selected then it is bad request
                raise SuperdeskApiError.badRequestError("Destination desk cannot be empty.")
            try:
                archived_doc = self.backend.find_one_raw(doc['guid'], doc['guid'])
            except FileNotFoundError as ex:
                raise ProviderError.externalProviderError(ex, provider)

            dest_doc = dict(archived_doc)
            new_id = generate_guid(type=GUID_TAG)
            new_guids.append(new_id)
            dest_doc['_id'] = new_id
            generate_unique_id_and_name(dest_doc)

            if provider:
                dest_doc['ingest_provider'] = str(provider[superdesk.config.ID_FIELD])

            dest_doc[config.VERSION] = 1
            send_to(doc=dest_doc, update=None, desk_id=doc.get('desk'), stage_id=doc.get('stage'))
            dest_doc[config.CONTENT_STATE] = doc.get('state', STATE_FETCHED)
            dest_doc[INGEST_ID] = archived_doc['_id']
            dest_doc[FAMILY_ID] = archived_doc['_id']
            remove_unwanted(dest_doc)
            set_original_creator(dest_doc)

            superdesk.get_resource_service(ARCHIVE).post([dest_doc])
            insert_into_versions(dest_doc.get('_id'))

        return new_guids

    def get(self, req, lookup):
        provider = get_resource_service('ingest_providers').find_one(source='aapmm', req=None)
        if provider:
            if 'config' in provider and 'username' in provider['config']:
                self.backend.set_credentials(provider['config']['username'], provider['config']['password'])
            query = self._get_query(req)
            results = self.backend.find('aapmm', query, None)
            for doc in results.docs:
                doc['ingest_provider'] = str(provider[superdesk.config.ID_FIELD])
            return results

    def _get_query(self, req):
        args = getattr(req, 'args', {})
        query = json.loads(args.get('source')) if args.get('source') else {'query': {'filtered': {}}}
        return query
