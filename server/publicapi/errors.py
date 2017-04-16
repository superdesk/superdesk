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
A module that contains exception types for the Superdesk public API.
"""


from superdesk.errors import SuperdeskError


class PublicApiError(SuperdeskError):
    """Base class for all Superdesk public API errors."""

    _codes = {
        10000: "Unknown API error.",
    }
    """A mapping of error codes to error messages."""

    def __init__(self, error_code=10000):
        super().__init__(error_code)


class UnknownParameterError(PublicApiError):
    """Used when request contains an unknown parameter."""

    PublicApiError._codes[10001] = "Unknown parameter."

    def __init__(self):
        super().__init__(10001)


class BadParameterValueError(PublicApiError):
    """Used when request contains a parameter with an invalid value."""

    PublicApiError._codes[10002] = "Bad parameter value."

    def __init__(self):
        super().__init__(10002)
