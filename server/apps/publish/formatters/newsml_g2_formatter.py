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
from superdesk.utc import utcnow
import superdesk
from superdesk.errors import FormatterError
from settings import NEWSML_PROVIDER_ID
from apps.publish.formatters.nitf_formatter import NITFFormatter


class NewsMLG2Formatter(Formatter):
    XML_ROOT = '<?xml version="1.0" encoding="UTF-8"?>'
    now = utcnow()
    string_now = now.strftime('%Y-%m-%dT%H:%M:%S.0000Z')

    _message_attrib = {'xmlns': 'http://iptc.org/std/nar/2006-10-01/', 'xmlns:x': 'http://www.w3.org/1999/xhtml',
                       'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

    _debug_message_extra = {'xsi:schemaLocation': 'http://iptc.org/std/nar/2006-10-01/ \
    http://www.iptc.org/std/NewsML-G2/2.18/specification/NewsML-G2_2.18-spec-All-Power.xsd'}

    def format(self, article, subscriber):
        try:
            pub_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)

            nitfFormater = NITFFormatter()
            nitf = nitfFormater.get_nitf(article, subscriber, pub_seq_num)

            self._message_attrib.update(self._debug_message_extra)
            newsMessage = etree.Element('newsMessage', attrib=self._message_attrib)
            self._format_header(article, newsMessage, pub_seq_num)
            itemSet = self._format_item(newsMessage)
            if article['type'] == 'text' or article['type'] == 'preformatted':
                self._format_newsitem(article, itemSet, nitf)

            return [(pub_seq_num, self.XML_ROOT + etree.tostring(newsMessage).decode('utf-8'))]
        except Exception as ex:
            raise FormatterError.newmsmlG2FormatterError(ex, subscriber)

    def _format_header(self, article, newsMessage, pub_seq_num):
        header = SubElement(newsMessage, 'header')
        SubElement(header, 'sent').text = self.string_now
        SubElement(header, 'sender').text = NEWSML_PROVIDER_ID
        # MAY NEED TO EXPAND THIS
        SubElement(header, 'transmitId').text = str(pub_seq_num)
        SubElement(header, 'origin').text = article.get('original_source', 'AAP')

    def _format_item(self, newsMessage):
        return SubElement(newsMessage, 'itemSet')

    def _format_newsitem(self, article, itemSet, nitf):
        newsItem = SubElement(itemSet, 'newsItem', attrib={'standard': 'NewsML-G2', 'standardversion': '2.18',
                                                           'guid': article['guid'],
                                                           'version': str(article[superdesk.config.VERSION]),
                                                           'xml:lang': article.get('language', 'en'),
                                                           'conformance': 'power'})
        SubElement(newsItem, 'catalogRef',
                   attrib={'href': 'http://www.iptc.org/std/catalog/catalog.IPTC-G2-Standards_25.xml”'})
        self._format_rights(newsItem, article)
        itemMeta = SubElement(newsItem, 'itemMeta')
        self._format_itemClass(article, itemMeta)
        self._format_provider(itemMeta)
        self._format_versioncreated(article, itemMeta)
        self._format_firstcreated(article, itemMeta)
        self._format_pubstatus(article, itemMeta)
        # optional properties
        # TODO Work out what to do with embargo, it may involve if we are publishing to media or none media
        # include the tag if the word embargoed is found in the ednote !!!!!
        self._format_ednote(article, itemMeta)
        self._format_signal(article, itemMeta)

        contentMeta = SubElement(newsItem, 'contentMeta')
        self._format_timestamps(article, contentMeta)
        # TODO located or locator codes are not yet defined
        self._format_creator(article, contentMeta)
        self._format_subject(article, contentMeta)
        self._format_genre(article, contentMeta)
        self._format_slugline(article, contentMeta)
        self._format_headline(article, contentMeta)

        contentSet = SubElement(newsItem, 'contentSet')
        if article['type'] == 'preformatted':
            inline = SubElement(contentSet, 'inlineData',
                                attrib={'contenttype': 'text/plain'}).text = article.get('body_html')
        elif article['type'] == 'text' or article['type'] == 'composite':
            inline = SubElement(contentSet, 'inlineXML',
                                attrib={'contenttype': 'application/nitf+xml'})
            inline.append(nitf)

    def _format_rights(self, newsItem, article):
        all_rights = superdesk.get_resource_service('vocabularies').find_one(req=None, _id='rightsinfo')
        rights_key = article.get('source', article.get('original_source', 'default'))
        default_rights = next(info for info in all_rights['items'] if info['name'] == 'default')
        rights = next((info for info in all_rights['items'] if info['name'] == rights_key), default_rights)
        rightsinfo = SubElement(newsItem, 'rightsInfo')
        holder = SubElement(rightsinfo, 'copyrightHolder')
        SubElement(holder, 'name').text = rights['copyrightHolder']
        SubElement(rightsinfo, 'copyrightNotice').text = rights['copyrightNotice']
        SubElement(rightsinfo, 'usageTerms').text = rights['usageTerms']

    # itemClass elements
    def _format_itemClass(self, article, itemMeta):
        if article['type'] == 'text' or article['type'] == 'preformatted' or article['type'] == 'composite':
            SubElement(itemMeta, 'itemClass', attrib={'qcode': 'ninat:text'})

    def _format_provider(self, itemMeta):
        provider = SubElement(itemMeta, 'provider')
        SubElement(provider, 'name').text = NEWSML_PROVIDER_ID

    def _format_versioncreated(self, article, itemMeta):
        SubElement(itemMeta, 'versionCreated').text = article['versioncreated'].strftime('%Y-%m-%dT%H:%M:%S+00:00')

    def _format_firstcreated(self, article, itemMeta):
        SubElement(itemMeta, 'firstCreated').text = article['firstcreated'].strftime('%Y-%m-%dT%H:%M:%S+00:00')

    def _format_pubstatus(self, article, itemMeta):
        SubElement(itemMeta, 'pubStatus', attrib={'qcode': 'stat:' + article.get('pubstatus', 'usable')})

    def _format_signal(self, article, itemMeta):
        if article['state'] == 'Corrected':
            SubElement(itemMeta, 'signal', attrib={'qcode': 'sig:correction'})
        else:
            SubElement(itemMeta, 'signal', attrib={'qcode': 'sig:update'})

    def _format_ednote(self, article, itemMeta):
        if 'ednote' in article and article.get('ednote', '') != '':
            SubElement(itemMeta, 'edNote').text = article.get('ednote', '')

    # contentMeta elements
    def _format_timestamps(self, article, contentMeta):
        SubElement(contentMeta, 'contentCreated').text = article['firstcreated'].strftime('%Y-%m-%dT%H:%M:%S+00:00')
        SubElement(contentMeta, 'contentModified').text = article['versioncreated'].strftime('%Y-%m-%dT%H:%M:%S+00:00')

    def _format_creator(self, article, contentMeta):
        if 'byline' in article:
            creator = SubElement(contentMeta, 'creator')
            SubElement(creator, 'name').text = article.get('byline', '')

    def _format_subject(self, article, contentMeta):
        if 'subject' in article and len(article['subject']) > 0:
            for s in article['subject']:
                if 'qcode' in s:
                    subj = SubElement(contentMeta, 'subject',
                                      attrib={'type': 'cpnat:abstract', 'qcode': 'subj:' + s['qcode']})
                    SubElement(subj, 'name', attrib={'xml:lang': 'en'}).text = s['name']

    def _format_genre(self, article, contentMeta):
        if 'genre' in article and len(article['genre']) > 0:
            for g in article['genre']:
                genre = SubElement(contentMeta, 'genre')
                SubElement(genre, 'name', attrib={'xml:lang': 'en'}).text = g.get('name', '')

    def _format_slugline(self, article, contentMeta):
        SubElement(contentMeta, 'slugline').text = article.get('slugline', '')

    def _format_headline(self, article, contentMeta):
        SubElement(contentMeta, 'headline').text = article.get('headline', '')

    def can_format(self, format_type, article):
        return format_type == 'newsmlg2' and article['type'] in ['text', 'preformatted', 'composite']
