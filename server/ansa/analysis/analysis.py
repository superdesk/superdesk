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

from flask import current_app as app
from superdesk.resource import Resource, not_analyzed, not_enabled
from superdesk.services import BaseService
from ansa.geonames import get_place_by_id


FORMAT_XML = "xml"
FORMAT_JSON = "json"
SEMANTICS_SCHEMA = {
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
        'placesExpanded': {'type': 'list'},
        'located': {'type': 'dict', 'mapping': not_enabled, 'nullable': True},
        'subjects': {'type': 'list'},
    }
}


def get_parent_product(qcode):
    if len(qcode) > 8:
        return qcode[:8]
    elif len(qcode) > 3:
        return qcode[:3]
    else:
        return None


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
        if key not in SEMANTICS_SCHEMA['schema']:
            continue
        items = []
        for item in val:
            if item.get('value'):
                items.append(item['value'])
            if key == 'iptcDomains' and item.get('id'):
                parsed['semantics']['iptcCodes'].append(item.get('id'))
                parsed['subject'].append({'name': item.get('value'), 'qcode': item.get('id')})
            if key == 'placesExpanded':
                place = item.get('comune') or item.get('provincia') or item.get('regione') or item.get('nazione')
                if place and place.get('code'):
                    parsed['place'].append(get_place_by_id(place['code']))
            if key == 'subjects':
                if item.get('qcode') and 'products:' in item['qcode'] and item.get('name'):
                    qcode = item['qcode'].replace('products:', '')
                    parsed['subject'].append({
                        'name': item.get('name'),
                        'qcode': qcode,
                        'scheme': 'products',
                        'parent': get_parent_product(qcode),
                    })
                    items.append(item.get('name'))

        parsed['semantics'][key] = items
    if parsed['semantics'].get('mainLemmas'):
        parsed['slugline'] = ''
        for item in parsed['semantics']['mainLemmas']:
            if len(parsed['slugline']) + len(item) < 50:
                parsed['slugline'] = ' '.join([parsed['slugline'], item])
            parsed.setdefault('keywords', []).append(item)
    for key, scheme in SEMANTICS_SCHEMA['schema'].items():
        if scheme.get('type') == 'list':
            parsed['semantics'].setdefault(key, [])
        elif scheme.get('type') == 'dict':
            parsed['semantics'].setdefault(key, None)
        elif scheme.get('type') == 'boolean':
            parsed['semantics'].setdefault(key, False)
    return parsed


def apply(analysed, item, skip_products=False):
    old_semantics = item.get('semantics', {})
    for key, val in analysed.items():
        if not item.get(key) and key != 'subject':
            item[key] = val
    if analysed.get('semantics'):
        item['semantics'] = analysed['semantics']
    if analysed.get('subject'):
        item.setdefault('subject', [])
        item['subject'] = [s for s in item['subject'] if s.get('scheme')]  # filter out iptc subjectcodes
        for subj in analysed['subject']:
            if subj.get('qcode') and (subj['qcode'], subj.get('scheme')) not in [
                    (s.get('qcode'), s.get('scheme')) for s in item['subject']
            ] and (subj.get('scheme') != 'products' or (item.get('type') == 'text' and not skip_products)):
                item['subject'].append(subj)
    if old_semantics and old_semantics.get('located'):  # keep located
        item.setdefault('semantics', {})
        item['semantics']['located'] = old_semantics['located']


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
            self.URL_EXTRACTION = URL_MAIN + "extractxsl.do"
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
        except (requests.exceptions.ReadTimeout, json.JSONDecodeError):
            return {}

    def apply(self, analysed, item, skip_products=False):
        return apply(analysed, item, skip_products=skip_products)

    def on_fetched(self, doc):
        doc.update(self.do_analyse(doc))
