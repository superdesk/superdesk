# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk import intrinsic_privilege
from .aap_mm_datalayer import AAPMMDatalayer
from apps.io.search_ingest import SearchIngestService, SearchIngestResource


def init_app(app):
    app.data.aapmm = AAPMMDatalayer(app)
    service = SearchIngestService(datasource=None, backend=app.data.aapmm, source='aapmm')
    SearchIngestResource(endpoint_name='aapmm', app=app, service=service)
    intrinsic_privilege(resource_name='aapmm', method=['GET', 'POST'])
