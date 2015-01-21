# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk import app
from datetime import timedelta
from superdesk.utc import utcnow
from eve.utils import date_to_str
import superdesk


class RemoveExpiredSessions():

    def run(self):
        self.remove_expired_sessions()

    def remove_expired_sessions(self):
        expiry_minutes = app.settings['SESSION_EXPIRY_MINUTES']
        expiration_time = utcnow() - timedelta(minutes=expiry_minutes)
        print('Deleting session not updated since {}'.format(expiration_time))
        query = {'_updated': {'$lte': date_to_str(expiration_time)}}
        superdesk.get_resource_service('auth').delete_all(query)
