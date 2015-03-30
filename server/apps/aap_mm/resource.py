# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import superdesk
import logging
from superdesk.resource import Resource

logger = logging.getLogger(__name__)


class AapMMResource(superdesk.Resource):
    resource_methods = ['GET', 'POST']
    schema = {
        'guid': {'type': 'string', 'required': True},
        'desk': Resource.rel('desks', False, nullable=True)
    }
