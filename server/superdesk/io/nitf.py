# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""Simple NITF parser"""

from datetime import datetime
from superdesk.io import Parser
import xml.etree.ElementTree as etree
from superdesk.errors import ParserError
from superdesk.utc import utc
from apps.content import CONTENT_TYPE, ITEM_TYPE
from superdesk.etree import get_word_count

subject_fields = ('tobject.subject.type', 'tobject.subject.matter', 'tobject.subject.detail')


def get_places(docdata):
    places = []
    evloc = docdata.find('evloc')
    if evloc is not None:
        places.append({
            'name': evloc.attrib.get('city'),
            'code': evloc.attrib.get('iso-cc'),
        })
    return places


def get_subjects(tree):
    subjects = []
    for elem in tree.findall('head/tobject/tobject.subject'):
        qcode = elem.get('tobject.subject.refnum')
        for field in subject_fields:
            if elem.get(field):
                subjects.append({
                    'name': elem.get(field)
                })

        if len(subjects):
            subjects[-1]['qcode'] = qcode
    return subjects


def get_keywords(docdata):
    return [keyword.attrib['key'] for keyword in docdata.findall('key-list/keyword')]


def get_content(tree):
    elements = []
    for elem in tree.find('body/body.content'):
        elements.append(etree.tostring(elem, encoding='unicode'))
    return ''.join(elements)


def get_norm_datetime(tree):
    if tree is None:
        return

    try:
        value = datetime.strptime(tree.attrib['norm'], '%Y%m%dT%H%M%S')
    except ValueError:
        value = datetime.strptime(tree.attrib['norm'], '%Y%m%dT%H%M%S%z')

    return utc.normalize(value) if value.tzinfo else value


def get_byline(tree):
    elem = tree.find('body/body.head/byline')
    byline = ''
    if elem is not None:
        byline = elem.text
        person = elem.find('person')
        if person is not None:
            byline = "{} {}".format(byline.strip(), person.text.strip())
    return byline


def parse_meta(tree, item):
    for elem in tree.findall('head/meta'):
        attribute_name = elem.get('name')

        if attribute_name == 'anpa-keyword':
            item['slugline'] = elem.get('content')
        elif attribute_name == 'anpa-sequence':
            item['ingest_provider_sequence'] = elem.get('content')
        elif attribute_name == 'anpa-category':
            item['anpa_category'] = [{'qcode': elem.get('content'), 'name': ''}]
        elif attribute_name == 'anpa-wordcount':
            item['word_count'] = int(elem.get('content'))
        elif attribute_name == 'anpa-takekey':
            item['anpa_take_key'] = elem.get('content')
        elif attribute_name == 'anpa-format':
            anpa_format = elem.get('content').lower() if elem.get('content') is not None else 'x'
            item[ITEM_TYPE] = CONTENT_TYPE.TEXT if anpa_format == 'x' else CONTENT_TYPE.PREFORMATTED


class NITFParser(Parser):
    """
    NITF Parser
    """

    def can_parse(self, xml):
        return xml.tag == 'nitf'

    def parse_message(self, tree, provider):
        item = {}
        try:
            docdata = tree.find('head/docdata')
            # set the default type.
            item[ITEM_TYPE] = CONTENT_TYPE.TEXT
            item['guid'] = item['uri'] = docdata.find('doc-id').get('id-string')
            item['urgency'] = int(docdata.find('urgency').get('ed-urg', '5'))
            item['pubstatus'] = (docdata.attrib.get('management-status', 'usable')).lower()
            item['firstcreated'] = get_norm_datetime(docdata.find('date.issue'))
            item['versioncreated'] = get_norm_datetime(docdata.find('date.issue'))
            item['expiry'] = get_norm_datetime(docdata.find('date.expire'))
            item['subject'] = get_subjects(tree)
            item['body_html'] = get_content(tree)
            item['place'] = get_places(docdata)
            item['keywords'] = get_keywords(docdata)

            if docdata.find('ed-msg') is not None:
                item['ednote'] = docdata.find('ed-msg').attrib.get('info')

            item['headline'] = tree.find('body/body.head/hedline/hl1').text

            elem = tree.find('body/body.head/abstract')
            item['abstract'] = elem.text if elem is not None else ''

            elem = tree.find('body/body.head/dateline/location/city')
            if elem is not None:
                self.set_dateline(item, city=elem.text)

            item['byline'] = get_byline(tree)

            parse_meta(tree, item)
            item.setdefault('word_count', get_word_count(item['body_html']))
            return item
        except Exception as ex:
            raise ParserError.nitfParserError(ex, provider)
