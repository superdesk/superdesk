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
import re
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from superdesk.publish.publish_service import PublishService
from superdesk.errors import FormatterError
import superdesk
from datetime import datetime
import pytz
import logging
logger = logging.getLogger(__name__)
tz = None

EMBED_RE = re.compile(r"<!-- EMBED START ([a-zA-Z]+ {id: \"(?P<id>.+?)\"}) -->.*"
                      r"<!-- EMBED END \1 -->", re.DOTALL)


class NTBNITFFormatter(NITFFormatter):
    XML_ROOT = '<?xml version="1.0" encoding="iso-8859-1" standalone="yes"?>'

    def can_format(self, format_type, article):
        """
        Method check if the article can be formatted to NTB NIT
        :param str format_type:
        :param dict article:
        :return: True if article can formatted else False
        """
        return format_type == 'ntbnitf' and article[ITEM_TYPE] == CONTENT_TYPE.TEXT

    def format(self, article, subscriber, codes=None, encoding="us-ascii"):
        global tz
        if tz is None:
            tz = pytz.timezone(superdesk.app.config['DEFAULT_TIMEZONE'])
        try:
            pub_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)
            nitf = self.get_nitf(article, subscriber, pub_seq_num)
            try:
                nitf.attrib['baselang'] = article['language']
            except KeyError:
                pass
            return [{'published_seq_num': pub_seq_num,
                     'formatted_item': self.XML_ROOT + ET.tostring(nitf, "unicode"),
                     'item_encoding': 'iso-8859-1'}]
        except Exception as ex:
            raise FormatterError.nitfFormatterError(ex, subscriber)

    def _get_ntb_category(self, article):
        category = ''
        for s in article.get('subject', []):
            if s.get('scheme') == 'category':
                category = s['qcode']
        return category

    def _get_ntb_subject(self, article):
        update = article['version'] - 1
        subject_prefix = "ny{}-".format(update) if update else ""
        return subject_prefix + article.get('slugline', '')

    def _format_tobject(self, article, head):
        return ET.SubElement(head, 'tobject', {'tobject.type': self._get_ntb_category(article)})

    def _format_docdata_dateissue(self, article, docdata):
        ET.SubElement(
            docdata,
            'date.issue',
            attrib={'norm': article['versioncreated'].astimezone(tz).strftime("%Y-%m-%dT%H:%M:%S")})

    def _format_docdata_doc_id(self, article, docdata):
        doc_id = "NTB{item_id}_{version:02}".format(
            item_id=article['item_id'],
            version=article['version'] - 1)
        ET.SubElement(docdata, 'doc-id', attrib={'regsrc': 'NTB', 'id-string': doc_id})

    def _format_date_expire(self, article, docdata):
        pass

    def _format_docdata(self, article, docdata):
        super()._format_docdata(article, docdata)

        if 'slugline' in article:
            key_list = ET.SubElement(docdata, 'key-list')
            ET.SubElement(key_list, 'keyword', attrib={'key': article['slugline']})
            ET.SubElement(docdata, 'du-key', attrib={'version': str(article['version']), 'key': article['slugline']})
        for place in article.get('place', []):
            evloc = ET.SubElement(docdata, 'evloc')
            for key, att in (('parent', 'state-prov'), ('qcode', 'county-dist')):
                try:
                    evloc.attrib[att] = place[key]
                except KeyError:
                    pass

    def _format_pubdata(self, article, head):
        pub_date = article['versioncreated'].astimezone(tz).strftime("%Y%m%dT%H%M%S")
        ET.SubElement(head, 'pubdata', attrib={'date.publication': pub_date})

    def _format_subjects(self, article, tobject):
        subjects = [s for s in article.get('subject', []) if s.get("scheme") == "subject_custom"]
        for subject in subjects:
            ET.SubElement(
                tobject,
                'tobject.subject',
                {'tobject.subject.refnum': subject.get('qcode', ''),
                 'tobject.subject.matter': subject.get('name', '')})

    def _format_datetimes(self, article, head):
            created = article['versioncreated'].astimezone(tz)
            ET.SubElement(head, 'meta', {'name': 'timestamp', 'content': created.strftime("%Y.%m.%d %H:%M:%S")})
            ET.SubElement(head, 'meta', {'name': 'ntb-dato', 'content': created.strftime("%d.%m.%Y %H:%M")})
            ET.SubElement(head, 'meta', {'name': 'NTBUtDato', 'content': created.strftime("%d.%m.%Y")})

    def _get_filename(self, article):
        """return filename as specified by NTB

        filename pattern: date_time_service_category_subject.xml
        example: 2016-08-16_11-07-46_Nyhetstjenesten_Innenriks_ny1-rygge-nedgang.xml
        """
        metadata = {}
        metadata['date'] = article['versioncreated'].astimezone(tz).strftime("%Y-%m-%d_%H-%M-%S")
        try:
            metadata['service'] = article['anpa_category'][0]['name']
        except (KeyError, IndexError):
            metadata['service'] = ""
        metadata['category'] = self._get_ntb_category(article)
        metadata['subject'] = self._get_ntb_subject(article)
        return "{date}_{service}_{category}_{subject}.{ext}".format(
            ext="xml",
            **metadata).replace(':', '-')

    def _format_meta(self, article, head, destination, pub_seq_num):
        super()._format_meta(article, head, destination, pub_seq_num)
        article['head'] = head  # needed to access head when formatting body content
        ET.SubElement(head, 'meta', {'name': 'NTBEditor', 'content': 'Superdesk'})
        try:
            service = article['anpa_category'][0]
        except (KeyError, IndexError):
            pass
        else:
            ET.SubElement(head, 'meta', {'name': 'NTBTjeneste', 'content': service.get("name", "")})
        ET.SubElement(head, 'meta', {'name': 'filename', 'content': self._get_filename(article)})

        self._format_datetimes(article, head)
        if 'slugline' in article:
            ET.SubElement(head, 'meta', {'name': 'NTBStikkord', 'content': article['slugline']})
        ET.SubElement(head, 'meta', {'name': 'subject', 'content': self._get_ntb_subject(article)})

        ET.SubElement(head, 'meta', {'name': 'NTBID', 'content': 'NTB{}'.format(article['item_id'])})

        # these static values never change
        ET.SubElement(head, 'meta', {'name': 'NTBDistribusjonsKode', 'content': 'ALL'})
        ET.SubElement(head, 'meta', {'name': 'NTBKanal', 'content': 'A'})

        # daily counter
        day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        pub_queue = superdesk.get_resource_service("publish_queue")
        daily_count = pub_queue.find({'transmit_started_at': {'$gte': day_start}}).count() + 1
        ET.SubElement(head, 'meta', {'name': 'NTBIPTCSequence', 'content': str(daily_count)})

    def _format_body_head_abstract(self, article, body_head):
        # abstract is added in body_content for NTB NITF
        pass

    def _format_body_head_dateline(self, article, body_head):
        try:
            dateline_content = article['dateline']['located']['city']
        except KeyError:
            pass
        else:
            dateline = ET.SubElement(body_head, 'dateline')
            dateline.text = dateline_content

    def _format_body_head_distributor(self, article, body_head):
        distrib = ET.SubElement(body_head, 'distributor')
        org = ET.SubElement(distrib, 'org')
        language = article['language']
        if language == 'nb-NO':
            org.text = 'NTB'
        elif language == 'nn-NO':
            org.text = 'NPK'

    def _add_media(self, body_content, type_, mime_type, source, caption):
        media = ET.SubElement(body_content, 'media')
        media.attrib['media-type'] = type_
        media_reference = ET.SubElement(media, 'media-reference')
        if mime_type is not None:
            media_reference.attrib['mime-type'] = mime_type
        media_reference.attrib['source'] = source
        media_caption = ET.SubElement(media, 'media-caption')
        media_caption.text = caption

    def _add_meta_media_counter(self, head, counter):
        # we need to add a <meta/> in header with the number of media
        # we first check index of first meta element to group them
        first_meta = head.find("meta")
        if first_meta is not None:
            index = list(head).index(first_meta)
        else:
            index = 1
        elem = ET.Element('meta', {'name': 'NTBBilderAntall', 'content': str(counter)})
        head.insert(index, elem)

    def _format_body_content(self, article, body_content):
        head = article.pop('head')

        # abstract
        if 'abstract' in article:
            p = ET.SubElement(body_content, 'p', {'lede': "true", 'class': "lead"})
            abstract_txt = BeautifulSoup(article.get('abstract'), 'html.parser').getText()
            p.text = abstract_txt

        # media
        media_data = []
        try:
            associations = article['associations']
        except KeyError:
            self._add_meta_media_counter(head, 0)
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
        # <p class="lead" lede="true"> is used by NTB for abstract
        # and it may be existing in body_html (from ingested items ?)
        # so we need to remove it here
        p_lead = html_elts.find('p[@class="lead"]')
        if p_lead is not None:
            p_lead.attrib['class'] = "txt"
            try:
                del p_lead.attrib['lede']
            except KeyError:
                pass

        try:
            footer_txt = article['body_footer']
        except KeyError:
            pass
        else:
            body_footer = ET.SubElement(html_elts, 'p', {'class': 'txt-ind'})
            body_footer.text = footer_txt
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

            if data['type'] in (CONTENT_TYPE.PICTURE, CONTENT_TYPE.GRAPHIC):
                type_ = 'image'
            elif data['type'] == CONTENT_TYPE.VIDEO:
                type_ = 'video'
            else:
                logger.warning("unhandled content type: {}".format(data['type']))
                continue
            mime_type = data.get('mimetype')
            if mime_type is None:
                # these default values need to be used if mime_type is not found
                mime_type = 'image/jpeg' if type_ == 'image' else 'video/mpeg'
            caption = data.get('description_text', '')
            self._add_media(body_content, type_, mime_type, source, caption)
        self._add_meta_media_counter(head, len(media_data))

    def _format_body_end(self, article, body_end):
        if article.get('sign_off'):
            tagline = ET.SubElement(body_end, 'tagline')
            a = ET.SubElement(tagline, 'a', {'href': article['sign_off']})
            a.text = article['sign_off']


PublishService.register_file_extension('ntbnitf', 'xml')
