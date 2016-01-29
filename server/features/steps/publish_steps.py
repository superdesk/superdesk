# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015, 2016 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from behave import when  # @UnresolvedImport
from apps.publish.enqueue import enqueue_published


@when('we enqueue published')
def step_impl_when_auth(context):
    enqueue_published.apply_async()
