# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from eve.utils import config
from superdesk.users import UsersService, UsersResource, is_admin  # NOQA


logger = logging.getLogger(__name__)


class ADUsersService(UsersService):
    """
    Service class for UsersResource and should be used when AD is active.
    """

    readonly_fields = ['email', 'phone', 'first_name', 'last_name']

    def on_fetched(self, doc):
        super().on_fetched(doc)
        for document in doc['_items']:
            self.set_defaults(document)

    def on_fetched_item(self, doc):
        super().on_fetched_item(doc)
        self.set_defaults(doc)

    def set_defaults(self, doc):
        """
        Set the readonly fields for LDAP user.
        :param dict doc: user
        """
        readonly = {}
        user_attributes = config.LDAP_USER_ATTRIBUTES
        for value in user_attributes.values():
            if value in self.readonly_fields:
                readonly[value] = True

        doc['_readonly'] = readonly
