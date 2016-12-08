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

    resource_methods = ['POST']
    privileges = {'POST': 'archive'}


class AnalysisService(BaseService):
    """Service analysing text"""

    def __init__(self, datasource=None, backend=None):
        super(AnalysisService, self).__init__(datasource, backend)
        self.URL_EXTRACTION = None

    def create(self, docs, **kwargs):
        ids = []
        for doc in docs:
            doc['semantics'] = self.do_analyse(doc)
            ids.append('')
        return ids

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
        return self.parse(extracted)

    def on_fetched(self, doc):
        doc.update(self.do_analyse(doc))

    def parse(self, extracted):
        parsed = {}
        for key, val in extracted.items():
            if not isinstance(val, list):
                parsed[key] = val
                continue
            items = []
            for item in val:
                if item.get('value'):
                    items.append(item['value'])
            parsed[key] = items
        return parsed
