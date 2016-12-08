# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.resource import Resource
from superdesk.services import BaseService
from flask import current_app as app
import json
import requests
try:
    import settings
except ImportError:
    # settings doesn't exist during tests
    settings = None
import logging

logger = logging.getLogger(__name__)

FORMAT_XML = "xml"
FORMAT_JSON = "json"


class AnalysisResource(Resource):
    schema = {
        'title': {
            'type': 'string',
            'required': False
        },
        'abstract': {
            'type': 'string',
            'required': False
        },
        'text': {
            'type': 'string',
            'required': True
        },
        'lang': {
            'type': 'string',
            'required': False
        },
    }


class AnalysisService(BaseService):
    """Service analysing text"""

    def __init__(self, datasource=None, backend=None):
        super(AnalysisService, self).__init__(datasource, backend)
        self.URL_EXTRACTION = None

    def do_analyse(self, doc):
        if self.URL_EXTRACTION is None:
            URL_MAIN = app.config["ANSA_ANALYSIS_URL"]
            self.URL_EXTRACTION = URL_MAIN + "extract.do"
        extraction_data = {
            "abstract": doc.get('abstract', ''),
            "lang": doc.get('lang', 'ENG'),
            "text": doc['text'],
            "title": doc.get('title', ''),
            "format": FORMAT_JSON,
        }
        r = requests.post(self.URL_EXTRACTION, extraction_data)
        extracted = json.loads(r.text)
        return extracted

    def on_fetched(self, doc):
        doc.update(self.do_analyse(doc))
