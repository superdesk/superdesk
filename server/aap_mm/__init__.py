# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from apps.search_providers import register_search_provider
from superdesk import intrinsic_privilege

PROVIDER_NAME = 'aapmm'


def init_app(app):
    # Must be imported here as the constant PROVIDER_NAME is referenced by the below modules
    from .aap_mm_datalayer import AAPMMDatalayer
    from .resource import AAPMMResource
    from .service import AAPMMService

    app.data.aapmm = AAPMMDatalayer(app)

    aapmm_service = AAPMMService(datasource=None, backend=app.data.aapmm)
    AAPMMResource(endpoint_name=PROVIDER_NAME, app=app, service=aapmm_service)

    intrinsic_privilege(resource_name=PROVIDER_NAME, method=['GET', 'POST'])


register_search_provider(name=PROVIDER_NAME, fetch_endpoint=PROVIDER_NAME)
