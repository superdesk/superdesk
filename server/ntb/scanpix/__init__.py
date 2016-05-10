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

from ntb.scanpix.scanpix_datalayer import ScanpixDatalayer
from apps.io.search_ingest import SearchIngestService, SearchIngestResource


def init_app(app):
    app.data.scanpix = ScanpixDatalayer(app)
    service = SearchIngestService(datasource=None, backend=app.data.scanpix, source='scanpix')
    SearchIngestResource(endpoint_name='scanpix', app=app, service=service)
    intrinsic_privilege(resource_name='scanpix', method=['GET', 'POST'])


register_search_provider(name='scanpix', fetch_endpoint='scanpix')
