# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk import utils as utils, get_resource_service
from superdesk.services import BaseService
from flask import current_app as app


class AuthService(BaseService):

    def authenticate(self, document):
        raise NotImplementedError()

    def on_create(self, docs):
        for doc in docs:
            user = self.authenticate(doc)

            self.set_auth_default(doc, user['_id'])

    def on_created(self, docs):
        for doc in docs:
            get_resource_service('preferences').set_session_based_prefs(doc['_id'], doc['user'])

    def on_deleted(self, doc):
        """
        :param doc: A deleted auth doc AKA a session
        :return:
        """
        # notify that the session has ended
        app.on_session_end(doc['user'], doc['_id'])

    def set_auth_default(self, doc, user_id):
        doc['user'] = user_id
        doc['token'] = utils.get_random_string(40)
        del doc['password']
