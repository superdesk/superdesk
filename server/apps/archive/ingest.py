# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.workflow import set_default_state
from .common import on_create_item, handle_existing_data
from eve.utils import config

from superdesk.io.ingest import IngestResource, IngestService, STATE_INGESTED  # NOQA


class AppIngestService(IngestService):
    def on_fetched(self, docs):
        """
        Items when ingested have different case for pubstatus.
        Overriding this to handle existing data in Mongo & Elastic
        """

        for item in docs[config.ITEMS]:
            handle_existing_data(item, doc_type='ingest')

    def on_create(self, docs):
        for doc in docs:
            set_default_state(doc, STATE_INGESTED)
            handle_existing_data(doc, doc_type='ingest')

        on_create_item(docs, repo_type='ingest')  # do it after setting the state otherwise it will make it draft
