# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import xml.etree.ElementTree as etree
from xml.etree.ElementTree import SubElement

from apps.publish.formatters import Formatter
import superdesk
from superdesk.errors import FormatterError


class NITFFormatter(Formatter):
    """
    NITF Formatter
    """
    XML_ROOT = '<?xml version="1.0"?><!DOCTYPE nitf SYSTEM "../dtd/nitf-3-2.dtd">'

    def format(self, article, subscriber):
        try:
            pub_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)

            nitf = self.get_nitf(article, subscriber, pub_seq_num)
            return [(pub_seq_num, self.XML_ROOT + etree.tostring(nitf).decode('utf-8'))]
        except Exception as ex:
            raise FormatterError.nitfFormatterError(ex, subscriber)

    def get_nitf(self, article, destination, pub_seq_num):
        nitf = etree.Element("nitf")
        head = SubElement(nitf, "head")
        body = SubElement(nitf, "body")
        body_head = SubElement(body, "body.head")
        body_content = SubElement(body, "body.content")
        body_content.text = article['body_html']
        body_end = SubElement(body, "body.end")

        etree.Element('doc-id', attrib={'id-string': article['guid']})

        self.__append_meta(article, head, destination, pub_seq_num)
        self.__format_head(article, head)
        self.__format_body_head(article, body_head)
        self.__format_body_end(article, body_end)
        return nitf

    def __format_head(self, article, head):
        title = SubElement(head, 'title')
        title.text = article['headline']

        tobject = SubElement(head, 'tobject', {'tobject.type': 'news'})
        self.__format_subjects(article, tobject)

        docdata = SubElement(head, 'docdata', {'management-status': article['pubstatus']})
        SubElement(docdata, 'urgency', {'id-string': str(article.get('urgency', ''))})
        SubElement(docdata, 'date.issue', {'norm': str(article.get('firstcreated', ''))})
        SubElement(docdata, 'date.expire', {'norm': str(article.get('expiry', ''))})

        self.__format_keywords(article, head)

    def __format_subjects(self, article, tobject):
        for subject in article.get('subject', []):
            SubElement(tobject, 'tobject.subject',
                       {'tobject.subject.refnum': subject.get('qcode', ''),
                        'tobject.subject.matter': subject['name']})

    def __format_keywords(self, article, head):
        if article.get('keywords'):
            keylist = SubElement(head, 'key-list')
            for keyword in article['keywords']:
                SubElement(keylist, 'keyword', {'key': keyword})

    def __format_body_head(self, article, body_head):
        hedline = SubElement(body_head, 'hedline')
        hl1 = SubElement(hedline, 'hl1')
        hl1.text = article['headline']

        if article.get('byline'):
            byline = SubElement(body_head, 'byline')
            byline.text = "By " + article['byline']

        if article.get('dateline'):
            dateline = SubElement(body_head, 'dateline')
            dateline.text = article['dateline'].get('text')

    def __format_body_end(self, article, body_end):
        if article.get('ednote'):
            tagline = SubElement(body_end, 'tagline')
            tagline.text = article['ednote']

    def can_format(self, format_type, article):
        return format_type == 'nitf' and article['type'] in ['text', 'preformatted', 'composite']

    def __append_meta(self, article, head, destination, pub_seq_num):
        """
        Appends <meta> elements to <head>
        """

        SubElement(head, 'meta', {'name': 'anpa-sequence', 'content': str(pub_seq_num)})
