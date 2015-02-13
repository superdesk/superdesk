# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""Privileges registry."""
from .errors import PrivilegeNameError

_privileges = {}
_intrinsic_privileges = {}


def privilege(**kwargs):
    """Register privilege.

    Privilege name must not contain "."

    Privilege properties:
    - name
    - label
    - description
    - category
    """
    if '.' in kwargs['name']:
        raise PrivilegeNameError('"." is not supported in privilege name "%s"' % kwargs['name'])
    _privileges[kwargs['name']] = kwargs


def get_privilege_list():
    """Get list of all registered privileges."""
    return [v for v in _privileges.values()]


def intrinsic_privilege(resource_name, method=[]):
    """
    Registers intrinsic privileges.
    """

    _intrinsic_privileges[resource_name] = method


def get_intrinsic_privileges():
    """Get list of all registered intrinsic privileges."""

    return _intrinsic_privileges
