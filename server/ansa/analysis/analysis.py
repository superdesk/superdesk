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


def parse(extracted):
    parsed = {
        'semantics': {'iptcCodes': []},
        'subject': [],
        'place': [],
        'abstract': '',
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
                parsed['place'].append({'name': item.get('value'), 'qcode': 'n:%s' % item.get('value')})
        parsed['semantics'][key] = items
    if parsed['semantics'].get('mainLemmas'):
        parsed['slugline'] = ''
        for item in parsed['semantics']['mainLemmas']:
            if len(parsed['slugline']) + len(item) < 50:
                parsed['slugline'] = ' '.join([parsed['slugline'], item])
    if parsed['semantics'].get('mainSenteces'):
        parsed['abstract'] = '\n'.join([
            '<p>%s</p>' % p for p in parsed['semantics']['mainSenteces']
        ])
    return parsed


def apply(analysed, item):
    for key, val in analysed.items():
        if not item.get(key):
            item[key] = val
    if analysed.get('semantics'):
        item['semantics'] = analysed['semantics']
    if analysed.get('subject'):
        item['subject'] = [s for s in item['subject'] if s.get('scheme')]  # filter out iptc subjectcodes
        item['subject'].extend(analysed['subject'])
    if analysed.get('abstract') and not item.get('abstract'):
        item.setdefault('abstract', analysed['abstract'])


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
            if not doc.get('abstract') and analysed.get('abstract'):
                doc['abstract'] = analysed['abstract']
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
            return parse(extracted)
        except requests.exceptions.ReadTimeout:
            return {}

    def apply(self, analysed, item):
        return apply(analysed, item)

    def on_fetched(self, doc):
        doc.update(self.do_analyse(doc))
