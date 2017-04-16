# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os
from publicapi.behave_setup import setup


def before_all(context):
    setup(context)
    os.environ['BEHAVE_TESTING'] = '1'


def before_feature(context, feature):
    pass


def before_scenario(context, scenario):
    config = {}
    if scenario.status != 'skipped' and 'notesting' in scenario.tags:
        config['SUPERDESK_TESTING'] = False

    setup(context, config)
    context.headers = [
        ('Content-Type', 'application/json'),
        ('Origin', 'localhost')
    ]


def after_scenario(context, scenario):
    pass
