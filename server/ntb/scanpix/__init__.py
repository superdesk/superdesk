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


# instances are hardcoded as they are also hardcoded in the backend
# FIXME: need to be refactored with SD-4448
instances = ['ntbtema', 'ntbkultur', 'desk', 'npk']


def init_app(app):
    for instance_name in instances:
        name = 'scanpix({})'.format(instance_name)
        scanpix = ScanpixDatalayer(app)
        service = SearchIngestService(datasource=None, backend=scanpix, source=name)
        SearchIngestResource(endpoint_name=name, app=app, service=service)
        intrinsic_privilege(resource_name=name, method=['GET', 'POST'])


for instance_name in instances:
    name = 'scanpix({})'.format(instance_name)
    register_search_provider(name=name, fetch_endpoint=name)
