# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import datetime
from superdesk.io import Parser
from superdesk.errors import ParserError
from superdesk.utc import utc


class WENNParser(Parser):
    """
    WENN Feed Parser and will return list of items.
    """
    ATOM_NS = 'http://www.w3.org/2005/Atom'
    WENN_MM_NS = 'http://feed.wenn.com/xmlns/2010/03/wenn_mm'
    WENN_NM_NS = 'http://feed.wenn.com/xmlns/2010/03/wenn_nm'
    WENN_CM_NS = 'http://feed.wenn.com/xmlns/2010/03/wenn_cm'
    GEORSS_NS = 'http://www.georss.org/georss'

    def can_parse(self, xml):
        return xml.tag == self.qname('feed', self.ATOM_NS) and \
            len(xml.findall(self.qname('NewsManagement', self.WENN_NM_NS))) > 0

    def parse_message(self, tree, provider):
        itemList = []
        try:
            for entry in tree.findall(self.qname('entry', self.ATOM_NS)):
                item = {}
                self.set_item_defaults(item)
                self.parse_content_management(item, entry)
                self.parse_news_management(item, entry)
                item['body_html'] = self.get_elem_content(entry.find(self.qname('content', self.ATOM_NS)))
                itemList.append(item)
            return itemList

        except Exception as ex:
            raise ParserError.wennParserError(ex, provider)

    def set_item_defaults(self, item):
        item['type'] = 'text'
        item['urgency'] = 5
        item['pubstatus'] = 'usable'
        item['anpa_category'] = [{'qcode': 'e'}]
        item['subject'] = [{'qcode': '01000000', 'name': 'arts, culture and entertainment'}]

    def parse_news_management(self, item, entry):
        news_mgmt_el = entry.find(self.qname('NewsManagement', self.WENN_NM_NS))
        if news_mgmt_el:
            item['firstcreated'] = self.datetime(self.get_elem_content(
                news_mgmt_el.find(self.qname('published', self.WENN_NM_NS))))
            item['versioncreated'] = self.datetime(self.get_elem_content(
                news_mgmt_el.find(self.qname('updated', self.WENN_NM_NS))))
            item['guid'] = self.get_elem_content(
                news_mgmt_el.find(self.qname('original_article_id', self.WENN_NM_NS)))

    def parse_content_management(self, item, entry):
        content_mgmt_el = entry.find(self.qname('ContentMetadata', self.WENN_CM_NS))
        if content_mgmt_el:
            item['headline'] = self.get_elem_content(content_mgmt_el.find(self.qname('title', self.WENN_CM_NS)))
            item['abstract'] = self.get_elem_content(
                content_mgmt_el.find(self.qname('first_line', self.WENN_CM_NS)))
            item['keywords'] = [element.attrib.get('value') for element in
                                content_mgmt_el.findall(self.qname('tags', self.WENN_CM_NS) + '/' +
                                                        self.qname('tag', self.WENN_CM_NS))
                                if element.attrib.get('value')]

    def get_elem_content(self, elem):
        return elem.text if elem is not None else ''

    def datetime(self, string):
        return datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S+00:00').replace(tzinfo=utc)
