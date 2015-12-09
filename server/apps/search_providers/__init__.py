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
from superdesk.errors import AlreadyExistsError

registered_search_providers = {}
allowed_search_providers = []


def init_app(app):
    # Must be imported here as the registered_search_providers is referenced by the below modules
    from .resource import SearchProviderResource
    from .service import SearchProviderService

    endpoint_name = 'search_providers'
    search_provider_service = SearchProviderService(endpoint_name, backend=superdesk.get_backend())
    SearchProviderResource(endpoint_name, app=app, service=search_provider_service)

    superdesk.privilege(name='search_providers', label='Manage Search Providers',
                        description='User can manage search providers.')


def register_search_provider(name, fetch_endpoint):
    """
    Registers a Search Provider with the given name and fetch_endpoint. Both have to be unique and if not raises
    AlreadyExistsError. The fetch_endpoint is used by clients to fetch the article from the Search Provider.

    :param name: Search Provider Name
    :type name: str
    :param fetch_endpoint: relative url to /api
    :type fetch_endpoint: str
    :raises: AlreadyExistsError - if a search has been registered with either name or fetch_endpoint.
    """

    if name in registered_search_providers:
        raise AlreadyExistsError("A Search Provider with name: {} already exists".format(name))

    if fetch_endpoint in registered_search_providers.values():
        raise AlreadyExistsError("A Search Provider for the fetch endpoint: {} exists with name: {}"
                                 .format(fetch_endpoint, registered_search_providers[name]))

    registered_search_providers[name] = fetch_endpoint
    allowed_search_providers.append(name)
