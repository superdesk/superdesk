# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from .macro_register import register  # NOQA
from .macros import MacrosResource, MacrosService


def init_app(app):
    MacrosResource('macros', app=app, service=MacrosService())
