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
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE, EMBARGO
from superdesk.utc import utcnow
import superdesk
from superdesk.errors import FormatterError
from settings import NEWSML_PROVIDER_ID
from apps.publish.formatters.nitf_formatter import NITFFormatter
from superdesk.metadata.packages import PACKAGE_TYPE


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
            is_package = self._is_package(article)
            self._message_attrib.update(self._debug_message_extra)
            self.news_message = etree.Element('newsMessage', attrib=self._message_attrib)
            news_message = self.news_message
            self._format_header(article, news_message, pub_seq_num)
            item_set = self._format_item(news_message)
            if is_package:
                item = self._format_item_set(article, item_set, 'packageItem')
                self._format_groupset(article, item)
            elif article[ITEM_TYPE] in {CONTENT_TYPE.PICTURE, CONTENT_TYPE.AUDIO, CONTENT_TYPE.VIDEO}:
                item = self._format_item_set(article, item_set, 'newsItem')
                self._format_contentset(article, item)
            else:
                nitfFormater = NITFFormatter()
                nitf = nitfFormater.get_nitf(article, subscriber, pub_seq_num)
                newsItem = self._format_item_set(article, item_set, 'newsItem')
                self._format_content(article, newsItem, nitf)

            return [(pub_seq_num, self.XML_ROOT + etree.tostring(news_message).decode('utf-8'))]
        except Exception as ex:
            raise FormatterError.newmsmlG2FormatterError(ex, subscriber)

    def _is_package(self, article):
        """
        Given an article returns if it is a none takes package or not
        :param artcile:
        :return: True is package
        """
        return article[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE and article.get(PACKAGE_TYPE, '') == ''

    def _format_header(self, article, news_message, pub_seq_num):
        """
        Creates the header element of the newsMessage.
        :param dict article:
        :param Element news_message:
        :param int pub_seq_num:
        """
        header = SubElement(news_message, 'header')
        SubElement(header, 'sent').text = self.string_now
        SubElement(header, 'sender').text = NEWSML_PROVIDER_ID
        SubElement(header, 'transmitId').text = str(pub_seq_num)
        SubElement(header, 'origin').text = article.get('original_source', 'AAP')
        SubElement(header, 'priority').text = str(article.get('priority', 5))

    def _format_item(self, news_message):
        return SubElement(news_message, 'itemSet')

    def _format_item_set(self, article, item_set, item_type):
        """
        Construct the item element (newsItem or packageItem) and append the item_meta and contentMeta entities
        :param dict article:
        :param element item_set:
        :param str item_type:
        """
        item = SubElement(item_set, item_type, attrib={'standard': 'NewsML-G2', 'standardversion': '2.18',
                                                       'guid': article['guid'],
                                                       'version': str(article[superdesk.config.VERSION]),
                                                       'xml:lang': article.get('language', 'en'),
                                                       'conformance': 'power'})
        SubElement(item, 'catalogRef',
                   attrib={'href': 'http://www.iptc.org/std/catalog/catalog.IPTC-G2-Standards_25.xml”'})
        self._format_rights(item, article)
        item_meta = SubElement(item, 'itemMeta')
        self._format_itemClass(article, item_meta)
        self._format_provider(item_meta)
        self._format_versioncreated(article, item_meta)
        self._format_firstcreated(article, item_meta)
        self._format_pubstatus(article, item_meta)

        if article.get(EMBARGO):
            SubElement(item_meta, 'embargoed').text = article[EMBARGO].isoformat()

        # optional properties
        self._format_ednote(article, item_meta)
        self._format_signal(article, item_meta)

        content_meta = SubElement(item, 'contentMeta')
        self._format_timestamps(article, content_meta)
        SubElement(content_meta, 'urgency').text = str(article.get('urgency', 5))
        self._format_creator(article, content_meta)
        self._format_located(article, content_meta)
        self._format_subject(article, content_meta)
        self._format_genre(article, content_meta)
        self._format_slugline(article, content_meta)
        self._format_headline(article, content_meta)
        self._format_place(article, content_meta)

        if article[ITEM_TYPE] in {CONTENT_TYPE.PICTURE, CONTENT_TYPE.AUDIO, CONTENT_TYPE.VIDEO}:
            self._format_description(article, content_meta)
            self._format_creditline(article, content_meta)
        return item

    def _format_content(self, article, newsItem, nitf):
        """
        Adds the content set to the xml
        :param article:
        :param newsItem:
        :param nitf:
        :return: xml with the nitf content appended
        """
        contentSet = SubElement(newsItem, 'contentSet')
        if article[ITEM_TYPE] == CONTENT_TYPE.PREFORMATTED:
            inline = SubElement(contentSet, 'inlineData',
                                attrib={'contenttype': 'text/plain'}).text = article.get('body_html')
        elif article[ITEM_TYPE] in [CONTENT_TYPE.TEXT, CONTENT_TYPE.COMPOSITE]:
            inline = SubElement(contentSet, 'inlineXML',
                                attrib={'contenttype': 'application/nitf+xml'})
            inline.append(nitf)

    def _format_rights(self, newsItem, article):
        """
        Adds the rightsholder section to the newsItem
        :param Element newsItem:
        :param dict article:
        """
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
    def _format_itemClass(self, article, item_meta):
        """
        Append the item class to the item_meta data element
        :param dict article:
        :param Element item_meta:
        """
        if CONTENT_TYPE.COMPOSITE and self._is_package(article):
            SubElement(item_meta, 'itemClass', attrib={'qcode': 'ninat:composite'})
            return
        if article[ITEM_TYPE] in {CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED, CONTENT_TYPE.COMPOSITE}:
            SubElement(item_meta, 'itemClass', attrib={'qcode': 'ninat:text'})
        elif article[ITEM_TYPE] in {CONTENT_TYPE.PICTURE, CONTENT_TYPE.AUDIO, CONTENT_TYPE.VIDEO}:
            SubElement(item_meta, 'itemClass', attrib={'qcode': 'ninat:%s' % article[ITEM_TYPE].lower()})

    def _format_provider(self, item_meta):
        """
        Appends the provider element to the item_meta element
        :param dict article:
        :param Element item_meta:
        """
        provider = SubElement(item_meta, 'provider')
        SubElement(provider, 'name').text = NEWSML_PROVIDER_ID

    def _format_versioncreated(self, article, item_meta):
        """
        Appends the versionCreated element to the item_meta element
        :param dict article:
        :param Element item_meta:
        """
        SubElement(item_meta, 'versionCreated').text = article['versioncreated'].strftime('%Y-%m-%dT%H:%M:%S+00:00')

    def _format_firstcreated(self, article, item_meta):
        """
        Appends the firstCreated element to the item_meta element
        :param dict article:
        :param Element item_meta:
        """
        SubElement(item_meta, 'firstCreated').text = article['firstcreated'].strftime('%Y-%m-%dT%H:%M:%S+00:00')

    def _format_pubstatus(self, article, item_meta):
        """
        Appends the pubStatus element to the item_meta element
        :param dict article:
        :param Element item_meta:
        """
        SubElement(item_meta, 'pubStatus', attrib={'qcode': 'stat:' + article.get('pubstatus', 'usable')})

    def _format_signal(self, article, item_meta):
        """
        Appends the signal element to the item_meta element
        :param dict article:
        :param Element item_meta:
        """
        if article['state'] == 'Corrected':
            SubElement(item_meta, 'signal', attrib={'qcode': 'sig:correction'})
        else:
            SubElement(item_meta, 'signal', attrib={'qcode': 'sig:update'})

    def _format_ednote(self, article, item_meta):
        """
        Appends the edNote element to the item_meta element
        :param dict article:
        :param Element item_meta:
        """
        if 'ednote' in article and article.get('ednote', '') != '':
            SubElement(item_meta, 'edNote').text = article.get('ednote', '')

    # contentMeta elements
    def _format_timestamps(self, article, content_meta):
        """
        Appends the contentCreated and contentModified element to the contentMeta element
        :param dict article:
        :param Element content_meta:
        """
        SubElement(content_meta, 'contentCreated').text = article['firstcreated'].strftime('%Y-%m-%dT%H:%M:%S+00:00')
        SubElement(content_meta, 'contentModified').text = article['versioncreated'].strftime('%Y-%m-%dT%H:%M:%S+00:00')

    def _format_creator(self, article, content_meta):
        """
        Appends the creator element to the contentMeta element
        :param dict article:
        :param Element content_meta:
        """
        if 'byline' in article:
            creator = SubElement(content_meta, 'creator')
            SubElement(creator, 'name').text = article.get('byline', '')

    def _format_subject(self, article, content_meta):
        """
        Appends the subject element to the contentMeta element
        :param dict article:
        :param Element content_meta:
        """
        if 'subject' in article and len(article['subject']) > 0:
            for s in article['subject']:
                if 'qcode' in s:
                    subj = SubElement(content_meta, 'subject',
                                      attrib={'type': 'cpnat:abstract', 'qcode': 'subj:' + s['qcode']})
                    SubElement(subj, 'name', attrib={'xml:lang': 'en'}).text = s['name']

    def _format_genre(self, article, content_meta):
        """
        Appends the genre element to the contentMeta element
        :param dict article:
        :param Element content_meta:
        """
        if 'genre' in article and len(article['genre']) > 0:
            for g in article['genre']:
                genre = SubElement(content_meta, 'genre')
                SubElement(genre, 'name', attrib={'xml:lang': 'en'}).text = g.get('name', '')

    def _format_slugline(self, article, content_meta):
        """
        Appends the slugline element to the contentMeta element
        :param dict article:
        :param Element content_meta:
        """
        SubElement(content_meta, 'slugline').text = article.get('slugline', '')

    def _format_headline(self, article, content_meta):
        """
        Appends the headline element to the contentMeta element
        :param dict article:
        :param Element content_meta:
        """
        SubElement(content_meta, 'headline').text = article.get('headline', '')

    def _format_place(self, article, content_meta):
        """
        Appends the subject (of type geoArea) element to the contentMeta element
        :param dict article:
        :param Element content_meta:
        """
        for location in article.get('place', []):
            if location.get('name'):
                subject = SubElement(content_meta, 'subject', attrib={'type': 'cpnat:geoArea'})
                SubElement(subject, 'name').text = location.get('name', '')

    def _format_located(self, article, content_meta):
        """
        Appends the located element to the contentMeta element
        :param dict article:
        :param Element content_meta:
        """
        located = article.get('dateline', {}).get('located', {})
        if located and located.get('city'):
            located_elm = SubElement(content_meta, 'located', attrib={'type': 'cptype:city'})
            SubElement(located_elm, "name").text = located.get('city')
            if located.get('state'):
                broader = SubElement(located_elm, "broader", attrib={'type': 'cptype:statprov'})
                SubElement(broader, "name").text = located.get('state')
            if located.get('country'):
                broader = SubElement(located_elm, "broader", attrib={'type': 'cptype:country'})
                SubElement(broader, "name").text = located.get('country')

        if article.get('dateline', {}).get('text', {}):
            SubElement(content_meta, 'dateline').text = article.get('dateline', {}).get('text', {})

    def _format_description(self, article, content_meta):
        """
        Appends the image description to the contentMeta element
        :param article:
        :param content_meta:
        """
        SubElement(content_meta, 'description', attrib={'role': 'drol:caption'}).text = article.get('description', '')

    def _format_creditline(self, article, content_meta):
        """
        Append the creditLine to the contentMeta for a picture
        :param article:
        :param content_meta:
        """
        SubElement(content_meta, 'creditline').text = article.get('original_source', '')

    def _format_groupset(self, article, item):
        """
        Constructs the groupSet element of a packageItem
        :param article:
        :param item:
        :return: groupSet appended to the item
        """
        groupSet = SubElement(item, 'groupSet', attrib={'root': 'root'})
        for group in article.get('groups', []):
            group_Elem = SubElement(groupSet, 'group', attrib={'id': group.get('id'), 'role': group.get('role')})
            for ref in group.get('refs', {}):
                if 'idRef' in ref:
                    SubElement(group_Elem, 'groupRef', attrib={'idref': ref.get('idRef')})
                else:
                    if 'residRef' in ref:
                        # get the current archive item being refered to
                        archive_item = superdesk.get_resource_service('archive').find_one(req=None,
                                                                                          _id=ref.get('residRef'))
                        if archive_item:
                            itemRef = SubElement(group_Elem, 'itemRef',
                                                 attrib={'residref': ref.get('guid'),
                                                         'contenttype': 'application/vnd.iptc.g2.newsitem+xml'})
                            SubElement(itemRef, 'itemClass', attrib={'qcode': 'ninat:' + ref.get('type', 'text')})
                            self._format_pubstatus(archive_item, itemRef)
                            self._format_headline(archive_item, itemRef)
                            self._format_slugline(archive_item, itemRef)

    def _format_contentset(self, article, item):
        """
        Constructs the contentSet element in a picture, video and audio newsItem.
        :param article:
        :param item:
        :return: contentSet Element added to the item
        """
        content_set = SubElement(item, 'contentSet')
        for rendition, value in article.get('renditions', {}).items():
            attrib = {'href': value.get('href'),
                      'contenttype': value.get('mimetype', value.get('mime_type', '')),
                      'rendition': 'rendition:' + rendition
                      }
            if article.get(ITEM_TYPE) == CONTENT_TYPE.PICTURE:
                if 'height' in value:
                    attrib['height'] = str(value.get('height'))
                if 'width' in value:
                    attrib['width'] = str(value.get('width'))
            elif article.get(ITEM_TYPE) in {CONTENT_TYPE.VIDEO, CONTENT_TYPE.AUDIO}:
                if article.get('filemeta', {}).get('width'):
                    attrib['width'] = str(article.get('filemeta', {}).get('width'))
                if article.get('filemeta', {}).get('height'):
                    attrib['height'] = str(article.get('filemeta', {}).get('height'))
                if article.get('filemeta', {}).get('duration'):
                    attrib['duration'] = article.get('filemeta', {}).get('duration')
                    attrib['durationunit'] = 'timeunit:normalPlayTime'

            if rendition == 'original' and 'filemeta' in article and 'length' in article['filemeta']:
                attrib['size'] = str(article.get('filemeta').get('length'))
            SubElement(content_set, 'remoteContent', attrib=attrib)

    def can_format(self, format_type, article):
        """
        Method check if the article can be formatted to NewsML G2 or not.
        :param str format_type:
        :param dict article:
        :return: True if article can formatted else False
        """
        return format_type == 'newsmlg2' and \
            article[ITEM_TYPE] in {CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED, CONTENT_TYPE.COMPOSITE,
                                   CONTENT_TYPE.PICTURE, CONTENT_TYPE.VIDEO, CONTENT_TYPE.AUDIO}
