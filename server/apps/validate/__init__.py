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

from .validate import ValidateService, ValidateResource
import superdesk

logger = logging.getLogger(__name__)


def init_app(app):
    endpoint_name = 'validate'
    service = ValidateService(endpoint_name, backend=None)
    ValidateResource(endpoint_name, app=app, service=service)

    superdesk.intrinsic_privilege(resource_name=endpoint_name, method=['POST'])
