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

from apps.search_providers import allowed_search_providers
from superdesk.errors import SuperdeskApiError
from superdesk.services import BaseService
from superdesk.utils import ListCursor

logger = logging.getLogger(__name__)


class SearchProviderService(BaseService):
    def get(self, req, lookup):
        """
        Overriding to filter out the providers if they haven't been registered with the application.
        """

        providers = list(super().get(req, lookup))
        filtered_providers = []

        for provider in providers:
            if provider['search_provider'] in allowed_search_providers:
                filtered_providers.append(provider)

        return ListCursor(filtered_providers)

    def find_one(self, req, **lookup):
        """
        Overriding to filter out the providers if they haven't been registered with the application.
        """

        provider = super().find_one(req, **lookup)
        return provider if provider and provider['search_provider'] in allowed_search_providers else None

    def on_delete(self, doc):
        """
        Overriding to check if the search provider being requested to delete has been used to fetch items.
        """

        if doc.get('last_item_update'):
            raise SuperdeskApiError.forbiddenError("Deleting a Search Provider after receiving items is prohibited.")
