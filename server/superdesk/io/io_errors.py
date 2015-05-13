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
import superdesk
from superdesk.io import provider_errors
from superdesk.publish import transmitter_errors
from superdesk.utils import ListCursor

logger = logging.getLogger(__name__)


class IOErrorsService(superdesk.Service):
    def get(self, req, lookup):
        """Return all ingest errors."""
        errors = provider_errors
        io_type = getattr(req, 'args', {}).get('io_type', 'ingest')
        if io_type == 'publish':
            errors = transmitter_errors

        source_type = getattr(req, 'args', {}).get('source_type')
        if source_type:
            return ListCursor([self.get_errors_by_source_type(source_type, errors)])
        else:
            return ListCursor([self.get_all_errors(errors)])

    def get_errors_by_source_type(self, source_type, errors):
        return {'source_errors': errors[source_type.lower()],
                'all_errors': self._get_all_errors(errors)}

    def get_all_errors(self, errors):
        return {'all_errors': self._get_all_errors(errors)}

    def _get_all_errors(self, errors):
        all_errors = {}
        for k, v in errors.items():
            all_errors.update(v)

        return all_errors


class IOErrorsResource(superdesk.Resource):
    resource_methods = ['GET']
    item_methods = []

    schema = {
        'ingest_error': {
            'type': 'string',
            'required': True
        },
        'source_type': {
            'type': 'string'
        },
        'io_type': {
            'type': 'string'
        }
    }
