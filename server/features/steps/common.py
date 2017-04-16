# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from behave import given, when, then  # @UnresolvedImport
from flask import json
from eve.methods.common import parse
from features.steps.steps import apply_placeholders, is_user_resource,\
    unique_headers, assert_200, test_json
from superdesk import get_resource_service
from superdesk.tests import get_prefixed_url


