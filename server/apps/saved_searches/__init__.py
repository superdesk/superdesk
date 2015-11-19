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
import superdesk
from .saved_searches import SavedSearchesService, SavedSearchesResource, AllSavedSearchesResource, \
    SavedSearchItemsResource, SavedSearchItemsService, AllSavedSearchesService

logger = logging.getLogger(__name__)


def init_app(app):
    endpoint_name = 'saved_searches'
    service = SavedSearchesService(endpoint_name, backend=superdesk.get_backend())
    SavedSearchesResource(endpoint_name, app=app, service=service)

    endpoint_name = 'all_saved_searches'
    service = AllSavedSearchesService(endpoint_name, backend=superdesk.get_backend())
    AllSavedSearchesResource(endpoint_name, app=app, service=service)

    endpoint_name = 'saved_search_items'
    service = SavedSearchItemsService(endpoint_name, backend=superdesk.get_backend())
    SavedSearchItemsResource(endpoint_name, app=app, service=service)

    superdesk.privilege(name='global_saved_searches',
                        label='Manage Global Saved Searches',
                        description='User can manage other users\' global saved searches')
    superdesk.privilege(name='saved_searches',
                        label='Manage Saved Searches',
                        description='User can manage saved searches')
