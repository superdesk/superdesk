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
from superdesk import app
from datetime import timedelta
from superdesk.utc import utcnow
from eve.utils import date_to_str
from superdesk import get_resource_service
import logging

logger = logging.getLogger(__name__)


class RemoveExpiredSessions(superdesk.Command):

    def run(self):
        self.remove_expired_sessions()

    def remove_expired_sessions(self):
        expiry_minutes = app.settings['SESSION_EXPIRY_MINUTES']
        expiration_time = utcnow() - timedelta(minutes=expiry_minutes)
        logger.info('Deleting session not updated since {}'.format(expiration_time))
        query = {'_updated': {'$lte': date_to_str(expiration_time)}}
        sessions = get_resource_service('auth').get(req=None, lookup=query)
        for session in sessions:
            get_resource_service('auth').delete_action({'_id': str(session['_id'])})
