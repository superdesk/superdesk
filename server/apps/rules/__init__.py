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

from .routing_rules import RoutingRuleSchemeResource, RoutingRuleSchemeService
from .rule_sets import RuleSetsService, RuleSetsResource
from superdesk import get_backend
import superdesk

logger = logging.getLogger(__name__)


def init_app(app):
    endpoint_name = 'rule_sets'
    service = RuleSetsService(endpoint_name, backend=get_backend())
    RuleSetsResource(endpoint_name, app=app, service=service)

    endpoint_name = 'routing_schemes'
    service = RoutingRuleSchemeService(endpoint_name, backend=get_backend())
    RoutingRuleSchemeResource(endpoint_name, app=app, service=service)

    superdesk.privilege(name='rule_sets', label='Transformation Rules Management',
                        description='User can setup transformation rules for ingest content.')

    superdesk.privilege(name='routing_rules', label='Routing Rules Management',
                        description='User can manage routing rules which are executed on ingested articles.')
