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
from superdesk.utc import utcnow
from settings import NEWSML_PROVIDER_ID


class NewsML12Formatter(Formatter):
    """
    NewsML 1.2 Formatter
    """
    XML_ROOT = '<?xml version="1.0"?><!DOCTYPE NewsML SYSTEM "http://www.aap.com.au/xml-res/NewsML_1.2.dtd">'
    now = utcnow()
    string_now = now.strftime('%Y%m%dT%H%M%S+0000')

    def format(self, article, subscriber):
        try:
            pub_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)

            newsml = etree.Element("NewsML")
            SubElement(newsml, "Catalog", {'Href': 'http://www.aap.com.au/xml-res/aap-master-catalog.xml'})
            news_envelope = SubElement(newsml, "NewsEnvelope")
            news_item = SubElement(newsml, "NewsItem")

            self._format_news_envelope(article, news_envelope, pub_seq_num)
            self._format_identification(article, news_item)
            self._format_news_management(article, news_item)
            self._format_news_component(article, news_item)

            return [(pub_seq_num, self.XML_ROOT + etree.tostring(newsml).decode('utf-8'))]
        except Exception as ex:
            raise FormatterError.newml12FormatterError(ex, subscriber)

    def _format_news_envelope(self, article, news_envelope, pub_seq_num):
        SubElement(news_envelope, 'TransmissionId').text = str(pub_seq_num)
        SubElement(news_envelope, 'DateAndTime').text = self.string_now
        SubElement(news_envelope, 'Priority', {'FormalName': article.get('priority', '')})

    def _format_identification(self, article, news_item):
        revision = self._process_revision(article)
        identification = SubElement(news_item, "Identification")
        news_identifier = SubElement(identification, "NewsIdentifier")
        SubElement(news_identifier, 'ProviderId').text = NEWSML_PROVIDER_ID
        SubElement(news_identifier, 'DateId').text = self.now.strftime("%Y%m%d")
        SubElement(news_identifier, 'NewsItemId').text = article['_id']
        SubElement(news_identifier, 'RevisionId', revision).text = str(article.get('_current_version', ''))
        SubElement(news_identifier, 'PublicIdentifier').text = article['_id']
        SubElement(identification, "DateLabel").text = self.now.strftime("%A %d %B %Y")

    def _process_revision(self, article):
        # Implementing the corrections
        # For the re-writes 'RelatesTo' field will be user
        revision = {'PreviousRevision': '0', 'Update': 'N'}
        if article['state'] == 'corrected':
            revision['PreviousRevision'] = str(article.get('_current_version') - 1)
            revision['Update'] = 'A'
        return revision

    def _format_news_management(self, article, news_item):
        news_management = SubElement(news_item, "NewsManagement")
        SubElement(news_management, 'NewsItemType', {'FormalName': 'News'})
        SubElement(news_management, 'FirstCreated').text = \
            article['firstcreated'].strftime('%Y%m%dT%H%M%S+0000')
        SubElement(news_management, 'ThisRevisionCreated').text = \
            article['versioncreated'].strftime('%Y%m%dT%H%M%S+0000')
        SubElement(news_management, 'Status', {'FormalName': article['pubstatus']})
        SubElement(news_management, 'Urgency', {'FormalName': str(article['urgency'])})
        if article['state'] == 'corrected':
            SubElement(news_management, 'Instruction', {'FormalName': 'Correction'})
        else:
            SubElement(news_management, 'Instruction', {'FormalName': 'Update'})

    def _format_news_component(self, article, news_item):
        news_component = SubElement(news_item, "NewsComponent")
        main_news_component = SubElement(news_component, "NewsComponent")
        SubElement(main_news_component, 'Role', {'FormalName': 'Main'})
        self._format_news_lines(article, main_news_component)
        self._format_rights_metadata(article, main_news_component)
        self._format_descriptive_metadata(article, main_news_component)
        self._format_abstract(article, main_news_component)
        self._format_body(article, main_news_component)

    def _format_news_lines(self, article, main_news_component):
        news_lines = SubElement(main_news_component, "NewsLines")
        SubElement(news_lines, 'Headline').text = article.get('headline', '')
        SubElement(news_lines, 'ByLine').text = article.get('byline', '')
        SubElement(news_lines, 'DateLine').text = article.get('dateline', {}).get('text', '')
        SubElement(news_lines, 'CreditLine').text = article.get('creditline', '')
        SubElement(news_lines, 'KeywordLine').text = article.get('slugline', '')

    def _format_rights_metadata(self, article, main_news_component):
        all_rights = superdesk.get_resource_service('vocabularies').find_one(req=None, _id='rightsinfo')
        rights_key = article.get('source', article.get('original_source', 'default'))
        default_rights = next(info for info in all_rights['items'] if info['name'] == 'default')
        rights = next((info for info in all_rights['items'] if info['name'] == rights_key), default_rights)

        rights_metadata = SubElement(main_news_component, "RightsMetadata")
        copyright = SubElement(rights_metadata, "Copyright")
        SubElement(copyright, 'CopyrightHolder').text = rights['copyrightHolder']
        SubElement(copyright, 'CopyrightDate').text = self.now.strftime("%Y")

        usage_rights = SubElement(rights_metadata, "UsageRights")
        SubElement(usage_rights, 'UsageType').text = rights['copyrightNotice']
        # SubElement(usage_rights, 'Geography').text = article.get('place', article.get('located', ''))
        SubElement(usage_rights, 'RightsHolder').text = article.get('source', article.get('original_source', ''))
        SubElement(usage_rights, 'Limitations').text = rights['usageTerms']
        SubElement(usage_rights, 'StartDate').text = self.string_now
        SubElement(usage_rights, 'EndDate').text = self.string_now

    def _format_descriptive_metadata(self, article, main_news_component):
        descriptive_metadata = SubElement(main_news_component, "DescriptiveMetadata")
        subject_code = SubElement(descriptive_metadata, "SubjectCode")

        for subject in article.get('subject', []):
            SubElement(subject_code, 'Subject', {'FormalName': subject.get('qcode', '')})

        if 'anpa_category' in article:
            for category in article.get('anpa_category', []):
                SubElement(descriptive_metadata, 'Property',
                           {'FormalName': 'Category', 'Value': category['qcode']})
        else:
            raise Exception('anpa category is missing')

        # TODO: Subcategory
        # TODO: Locator

    def _format_abstract(self, article, main_news_component):
        abstract_news_component = SubElement(main_news_component, "NewsComponent")
        SubElement(abstract_news_component, 'Role', {'FormalName': 'Abstract'})
        content_item = SubElement(abstract_news_component, "ContentItem")
        SubElement(content_item, 'MediaType', {'FormalName': 'Text'})
        SubElement(content_item, 'Format', {'FormalName': 'Text'})
        SubElement(content_item, 'DataContent').text = article.get('abstract', '')

    def _format_body(self, article, main_news_component):
        body_news_component = SubElement(main_news_component, "NewsComponent")
        SubElement(body_news_component, 'Role', {'FormalName': 'BodyText'})
        SubElement(body_news_component, 'Format', {'FormalName': 'Text'})
        content_item = SubElement(body_news_component, "ContentItem")
        SubElement(content_item, 'MediaType', {'FormalName': 'Text'})
        SubElement(content_item, 'Format', {'FormalName': 'Text'})
        SubElement(content_item, 'DataContent').text = article.get('body_html', '')

    def can_format(self, format_type, article):
        return format_type == 'newsml12' and article['type'] in ['text', 'preformatted', 'composite']
