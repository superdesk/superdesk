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
from apps.publish.publish_filters.filter_condition import FilterConditionService, FilterConditionResource, \
    FilterConditionParametersResource, FilterConditionParametersService
from apps.publish.publish_filters.publish_filter import PublishFilterService, PublishFilterResource
from apps.publish.publish_filters.publish_filter import PublishFilterTestResource, PublishFilterTestService

logger = logging.getLogger(__name__)


def init_app(app):
    endpoint_name = 'filter_conditions'
    service = FilterConditionService(endpoint_name, backend=get_backend())
    FilterConditionResource(endpoint_name, app=app, service=service)

    endpoint_name = 'filter_condition_parameters'
    service = FilterConditionParametersService(endpoint_name, backend=get_backend())
    FilterConditionParametersResource(endpoint_name, app=app, service=service)

    endpoint_name = 'publish_filters'
    service = PublishFilterService(endpoint_name, backend=get_backend())
    PublishFilterResource(endpoint_name, app=app, service=service)

    endpoint_name = 'publish_filter_tests'
    service = PublishFilterTestService(endpoint_name, backend=superdesk.get_backend())
    PublishFilterTestResource(endpoint_name, app=app, service=service)

    superdesk.privilege(name='publish_filters', label='Publish Filters',
                        description='User can manage publish filters')
