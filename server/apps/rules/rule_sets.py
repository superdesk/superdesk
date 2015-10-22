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

from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.errors import SuperdeskApiError


logger = logging.getLogger(__name__)


class RuleSetsResource(Resource):
    schema = {
        'name': {
            'type': 'string',
            'iunique': True,
            'required': True,
            'nullable': False,
            'empty': False,
            'minlength': 1
        },
        'rules': {
            'type': 'list'
        }
    }

    privileges = {'POST': 'rule_sets', 'DELETE': 'rule_sets', 'PATCH': 'rule_sets'}


class RuleSetsService(BaseService):

    def update(self, id, updates, original):
        """
        Overriding to set the value of "new" attribute of rules to empty string if it's None.
        """

        for rule in updates.get('rules', {}):
            if rule['new'] is None:
                rule['new'] = ''

        return super().update(id, updates, original)

    def on_delete(self, doc):
        if self.backend.find_one('ingest_providers', req=None, rule_set=doc['_id']):
            raise SuperdeskApiError.forbiddenError("Cannot delete Rule set as it's associated with channel(s).")
