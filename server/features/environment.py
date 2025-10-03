# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.tests.environment import (
    before_all as _before_all,
    before_feature,
    before_scenario,
    before_step,
    after_scenario,
)  # noqa
from superdesk.tests.environment import setup_before_all
from settings import INSTALLED_APPS


def before_all(context):
    config = {
        "INSTALLED_APPS": INSTALLED_APPS,
    }
    setup_before_all(context, config, app_factory=None)
    _before_all(context)
