# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import json
import requests
import requests.exceptions

from superdesk.resource import Resource
from superdesk.services import BaseService
from flask import current_app as app


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
            analysed = self.do_analyse(doc)
            for key, val in analysed.items():
                doc.setdefault(key, val)
            doc['semantics'] = analysed['semantics']
            ids.append('')
        return ids

    def do_analyse(self, doc):
        if self.URL_EXTRACTION is None:
            URL_MAIN = app.config["ANSA_ANALYSIS_URL"]
            self.URL_EXTRACTION = URL_MAIN + "extract.do"
        extraction_data = {
            "abstract": doc.get('abstract', ''),
            "lang": doc.get('lang', 'ITA'),
            "text": doc['text'],
            "title": doc.get('title', ''),
            "format": FORMAT_JSON,
        }
        try:
            r = requests.post(self.URL_EXTRACTION, extraction_data, timeout=(5, 30))
            extracted = json.loads(r.text)
            return self.parse(extracted)
        except requests.exceptions.ReadTimeout:
            return {}

    def on_fetched(self, doc):
        doc.update(self.do_analyse(doc))

    def parse(self, extracted):
        parsed = {
            'semantics': {'iptcCodes': []},
            'subject': [],
            'place': [],
        }
        for key, val in extracted.items():
            if not isinstance(val, list):
                continue
            items = []
            for item in val:
                if item.get('value'):
                    items.append(item['value'])
                if key == 'iptcDomains' and item.get('id'):
                    parsed['semantics']['iptcCodes'].append(item.get('id'))
                    parsed['subject'].append({'name': item.get('value'), 'qcode': item.get('id')})
                if key == 'places':
                    parsed['place'].append({'name': item.get('value')})
            parsed['semantics'][key] = items
        if parsed['semantics'].get('mainLemmas'):
            parsed['slugline'] = ''
            for item in parsed['semantics']['mainLemmas']:
                if len(parsed['slugline']) + len(item) < 50:
                    parsed['slugline'] = ' '.join([parsed['slugline'], item])
        return parsed
