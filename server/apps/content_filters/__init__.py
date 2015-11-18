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
from superdesk import get_backend

from apps.content_filters.filter_condition import (
    FilterConditionResource, FilterConditionService,
    FilterConditionParametersResource, FilterConditionParametersService)

from apps.content_filters.content_filter import (
    ContentFilterResource, ContentFilterService,
    ContentFilterTestResource, ContentFilterTestService)


logger = logging.getLogger(__name__)


def init_app(app):
    endpoint_name = 'filter_conditions'
    service = FilterConditionService(endpoint_name, backend=get_backend())
    FilterConditionResource(endpoint_name, app=app, service=service)

    endpoint_name = 'filter_condition_parameters'
    service = FilterConditionParametersService(
        endpoint_name, backend=get_backend())
    FilterConditionParametersResource(endpoint_name, app=app, service=service)

    endpoint_name = 'content_filters'
    service = ContentFilterService(endpoint_name, backend=get_backend())
    ContentFilterResource(endpoint_name, app=app, service=service)

    endpoint_name = 'content_filter_tests'
    service = ContentFilterTestService(
        endpoint_name, backend=superdesk.get_backend())
    ContentFilterTestResource(endpoint_name, app=app, service=service)

    superdesk.privilege(name='content_filters', label='Content Filters',
                        description='User can manage content filters')
