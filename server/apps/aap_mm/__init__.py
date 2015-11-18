# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from .service import AapMMService
from .resource import AapMMResource
from superdesk import intrinsic_privilege
from .aap_mm_datalayer import AAPMMDatalayer


def init_app(app):
    app.data.aapmm = AAPMMDatalayer(app)
    service = AapMMService(datasource=None, backend=app.data.aapmm)
    AapMMResource(endpoint_name='aapmm', app=app, service=service)
    intrinsic_privilege(resource_name='aapmm', method=['GET', 'POST'])
