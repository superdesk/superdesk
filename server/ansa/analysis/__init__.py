# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2016 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk

from .analysis import AnalysisResource, AnalysisService
from superdesk.resource import not_analyzed


def init_app(app):
    endpoint_name = 'analysis'
    service = AnalysisService(endpoint_name, backend=superdesk.get_backend())
    AnalysisResource(endpoint_name, app=app, service=service)

    semantics_schema = {
        'type': 'dict',
        'schema': {
            'iptcCodes': {'type': 'list', 'mapping': not_analyzed},
            'iptcDomains': {'type': 'list', 'mapping': not_analyzed},
            'newsDomains': {'type': 'list', 'mapping': not_analyzed},
            'places': {'type': 'list', 'mapping': not_analyzed},
            'persons': {'type': 'list'},  # enable analyzer
            'organizations': {'type': 'list', 'mapping': not_analyzed},
            'mainGroups': {'type': 'list', 'mapping': not_analyzed},
            'mainLemmas': {'type': 'list', 'mapping': not_analyzed},
            'mainSenteces': {'type': 'list'},
            'isMOODneutral': {'type': 'boolean'},
            'isMOODnegative': {'type': 'boolean'},
            'isMOODpositive': {'type': 'boolean'},
            'saos': {'type': 'list', 'mapping': not_analyzed},
            'sentimental': {'type': 'list', 'mapping': not_analyzed},
        }
    }

    for resource in ['ingest', 'archive', 'published', 'archive_autosave']:
        app.config['DOMAIN'][resource]['schema'].update({'semantics': semantics_schema})

    app.config['DOMAIN']['content_templates_apply']['schema']['item']['schema'].update(
        {'semantics': semantics_schema}
    )
