# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from superdesk.services import BaseService
from superdesk import get_resource_service
from apps.preferences import _session_preferences_key

"""Superdesk Users"""
from superdesk.resource import Resource


class UserSessionsResource(Resource):
    schema = {
    }
    datasource = {
        'source': 'users',
        'projection': {
            'username': 1,
            'session_preferences': 1
        }
    }
    resource_methods = []
    item_methods = ['GET', 'DELETE']
    privileges = {'DELETE': 'users'}


class UserSessionsService(BaseService):

    def delete(self, lookup):
        """
        Overriding the method to delete all user sessions for current user
        """
        user_id = str(lookup['_id'])
        user = get_resource_service('users').find_one(req=None, _id=user_id)
        for sessionId in user.get(_session_preferences_key, {}).keys():
            get_resource_service('auth').delete({'_id': sessionId})
        get_resource_service('users').patch(user['_id'], {_session_preferences_key: {}})
