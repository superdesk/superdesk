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
from superdesk import get_backend
from apps.publish.publish_filters.filter_condition import FilterConditionService, FilterConditionResource
from apps.publish.publish_filters.publish_filter import PublishFilterService, PublishFilterResource

logger = logging.getLogger(__name__)


def init_app(app):
    endpoint_name = 'filter_condition'
    service = FilterConditionService(endpoint_name, backend=get_backend())
    FilterConditionResource(endpoint_name, app=app, service=service)

    endpoint_name = 'publish_filter'
    service = PublishFilterService(endpoint_name, backend=get_backend())
    PublishFilterResource(endpoint_name, app=app, service=service)