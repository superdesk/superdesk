# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE
from superdesk.publish.formatters.nitf_formatter import NITFFormatter
from xml.etree.ElementTree import SubElement
import re
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
import logging
logger = logging.getLogger(__name__)

EMBED_RE = re.compile(r"<!-- EMBED START ([a-zA-Z]+ {id: \"(?P<id>.+?)\"}) -->.*"
                      r"<!-- EMBED END \1 -->", re.DOTALL)


class NTBNITFFormatter(NITFFormatter):

    def can_format(self, format_type, article):
        """
        Method check if the article can be formatted to NTB NIT
        :param str format_type:
        :param dict article:
        :return: True if article can formatted else False
        """
        return format_type == 'ntbnitf' and article[ITEM_TYPE] == CONTENT_TYPE.TEXT

    def _format_tobject(self, article, head):
        category = ''
        for s in article.get('subject', []):
            if s.get('scheme') == 'category':
                category = s['qcode']
        return SubElement(head, 'tobject', {'tobject.type': category})

    def _format_docdata(self, article, docdata):
        super()._format_docdata(article, docdata)
        if 'slugline' in article:
            SubElement(docdata, 'du-key', attrib={'version': '1', 'key': article['slugline']})

    def _format_subjects(self, article, tobject):
        subjects = [s for s in article.get('subject', []) if s.get("scheme") == "subject_custom"]
        for subject in subjects:
            SubElement(tobject, 'tobject.subject',
                       {'tobject.subject.refnum': subject.get('qcode', ''),
                        'tobject.subject.type': subject.get('name', '')})

    def _append_meta_priority(self, article, head):
        if 'priority' in article:
            SubElement(head, 'meta', {'name': 'NTBPrioritet', 'content': str(article['priority'])})

    def _append_meta(self, article, head, destination, pub_seq_num):
        super()._append_meta(article, head, destination, pub_seq_num)
        try:
            service = article['anpa_category'][0]
        except (KeyError, IndexError):
            pass
        else:
            SubElement(head, 'meta', {'name': 'NTBTjeneste', 'content': service.get("name", "")})

    def _format_body_head_abstract(self, article, body_head):
        # abstract is added in body_content for NTB NITF
        pass

    def _add_media(self, body_content, type_, mime_type, source, caption):
        media = SubElement(body_content, 'media')
        media.attrib['media_type'] = type_
        media_reference = SubElement(media, 'media-reference')
        if mime_type is not None:
            media_reference.attrib['mime-type'] = mime_type
        media_reference.attrib['source'] = source
        media_caption = SubElement(media, 'media-caption')
        media_caption.text = caption

    def _format_body_content(self, article, body_content):
        # abstract
        if 'abstract' in article:
            p = SubElement(body_content, 'p', {'lede': "true", 'class': "lead"})
            self.map_html_to_xml(p, article.get('abstract'))

        # media
        media_data = []
        try:
            associations = article['associations']
        except KeyError:
            return

        try:
            media_data.append(associations['featureimage'])
        except KeyError:
            try:
                media_data.append(associations['featuremedia'])
            except KeyError:
                pass

        def repl_embedded(match):
            """embedded in body_html handling"""
            # this method do 2 important things:
            # - it remove the embedded from body_html
            # - it fill media_data with embedded data in order of appearance
            id_ = match.group("id")
            try:
                data = associations[id_]
            except KeyError:
                logger.warning("Expected association {} not found!".format(id_))
            else:
                media_data.append(data)
            return ''

        html = EMBED_RE.sub(repl_embedded, article['body_html'])

        # at this point we have media data filled in right order
        # and no more embedded in html

        # regular content

        # we first convert the HTML to XML with BeautifulSoup
        # then parse it again with ElementTree
        # this is not optimal, but Beautiful Soup and etree are used
        # and etree from stdlib doesn't have a proper HTML parser
        soup = BeautifulSoup(html, 'html.parser')
        html_elts = ET.fromstring('<div>{}</div>'.format(soup.decode(formatter='xml')))
        body_content.extend(html_elts)

        # media
        for data in media_data:
            if 'scanpix' in data.get('fetch_endpoint', ''):
                # NTB request that Scanpix ID is used
                # in source for Scanpix media (see SDNTB-229)
                source = data['guid']
            else:
                try:
                    source = data['renditions']['original']['href']
                except KeyError:
                    try:
                        source = next(iter(data['renditions'].values()))['href']
                    except (StopIteration, KeyError):
                        logger.warning("Can't find source for media {}".format(data.get('guid', '')))
                        continue
            type_ = 'image' if data['type'] == 'picture' else 'video'
            mime_type = data.get('mimetype')
            caption = data.get('description_text', '')
            self._add_media(body_content, type_, mime_type, source, caption)
