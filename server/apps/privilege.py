# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from operator import itemgetter

import superdesk
from superdesk.utils import ListCursor
from superdesk.privilege import get_privilege_list


class PrivilegeService(superdesk.Service):

    def get(self, req, lookup):
        """
        Returns all registered privileges.
        """

        _privileges = get_privilege_list()
        _privileges = sorted(_privileges, key=itemgetter('label'))

        return ListCursor(_privileges)


class PrivilegeResource(superdesk.Resource):
    """Read-only resource with all privileges."""
    resource_methods = ['GET']
    item_methods = []


def init_app(app):
    PrivilegeResource('privileges', app=app, service=PrivilegeService())
