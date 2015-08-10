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
from flask import request


class WorkspaceResource(superdesk.Resource):

    schema = {
        'name': {'type': 'string', 'unique_to_user': True},
        'widgets': {'type': 'list'},
        'desk': superdesk.Resource.rel('desks'),
        'user': superdesk.Resource.rel('users'),
    }
    item_methods = ['GET', 'PATCH', 'DELETE']


class WorkspaceService(superdesk.Service):

    def is_authorized(self, **kwargs):
        if kwargs.get('_id'):
            data = self.find_one(req=None, _id=kwargs.get('_id')) or request.get_json()
        else:
            data = request.get_json()
        # TODO(petr): use privileges to test who can save desk/role dashboard
        return 'user' not in data or str(data['user']) == str(kwargs['user_id'])
