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

from pa.pa_img.pa_img_datalayer import PaImgDatalayer
from apps.io.search_ingest import SearchIngestService, SearchIngestResource


def init_app(app):
    app.data.paimg = PaImgDatalayer(app)
    service = SearchIngestService(datasource=None, backend=app.data.paimg, source='paimg')
    SearchIngestResource(endpoint_name='paimg', app=app, service=service)
    intrinsic_privilege(resource_name='paimg', method=['GET', 'POST'])


register_search_provider(name='paimg', fetch_endpoint='paimg')
