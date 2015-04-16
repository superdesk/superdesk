# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""
A module that provides the Superdesk public API application object.

The object is a normal `Flask <http://flask.pocoo.org/>`_ application (or, to
be more specific, an `Eve framework <http://python-eve.org/>`_ application).
"""


import os

from eve import Eve
from publicapi.datalayer import ApiDataLayer


_script_directory = os.path.dirname(os.path.realpath(__file__))

app = Eve(
    settings=os.path.join(_script_directory, 'settings.py'),
    data=ApiDataLayer,
)
