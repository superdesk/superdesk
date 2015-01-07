# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk import utils as utils
from superdesk.errors import UserInactiveError
from superdesk.services import BaseService


class AuthService(BaseService):

    def authenticate(self, document):
        raise NotImplementedError()

    def on_create(self, docs):
        for doc in docs:
            user = self.authenticate(doc)

            if not user.get('is_active', False):
                raise UserInactiveError()

            self.set_auth_default(doc, user['_id'])

    def set_auth_default(self, doc, id):
        doc['user'] = id
        doc['token'] = utils.get_random_string(40)
        del doc['password']
