# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.tests import TestCase
from apps.publish.formatters.newsml_1_2_formatter import NewsML12Formatter
import xml.etree.ElementTree as etree
import datetime
from nose.tools import assert_raises
from superdesk.errors import FormatterError
from apps.publish import init_app


class Newsml12FormatterTest(TestCase):

    article = {
        'source': 'AAP',
        'anpa_category': [{'qcode': 'a'}],
        'headline': 'This is a test headline',
        'byline': 'joe',
        'slugline': 'slugline',
        'subject': [{'qcode': '02011001'}, {'qcode': '02011002'}],
        'anpa_take_key': 'take_key',
        'unique_id': '1',
        'type': 'preformatted',
        'body_html': 'The story body',
        'type': 'text',
        'word_count': '1',
        'priority': '1',
        '_id': 'urn:localhost.abc',
        'state': 'published',
        'urgency': 2,
        'pubstatus': 'usable',
        'dateline': {'text': 'sample dateline'},
        'creditline': 'sample creditline',
        'keywords': ['traffic'],
        'abstract': 'sample abstract',
        'place': 'Australia'
    }

    vocab = [{'_id': 'rightsinfo', 'items': [{'name': 'AAP',
                                              'copyrightHolder': 'copy right holder',
                                              'copyrightNotice': 'copy right notice',
                                              'usageTerms': 'terms'},
                                             {'name': 'default',
                                              'copyrightHolder': 'default copy right holder',
                                              'copyrightNotice': 'default copy right notice',
                                              'usageTerms': 'default terms'}]}]

    now = datetime.datetime(2015, 6, 13, 11, 45, 19, 0)

    def setUp(self):
        super().setUp()
        self.article['state'] = 'published'
        self.article['firstcreated'] = self.now
        self.article['versioncreated'] = self.now
        self.newsml = etree.Element("NewsML")
        self.formatter = NewsML12Formatter()
        self.formatter.now = self.now
        self.formatter.string_now = self.now.strftime('%Y%m%dT%H%M%S+0000')
        with self.app.app_context():
            init_app(self.app)
            self.app.data.insert('vocabularies', self.vocab)

    def test_newsml_formatter_raises_error(self):
        with self.app.app_context():
            with assert_raises(FormatterError):
                self.article.pop('anpa_category', None)
                self.formatter.format(self.article, {'name': 'Test Subscriber'})

    def test_format_news_envelope(self):
        self.formatter._format_news_envelope(self.article, self.newsml, 7)
        self.assertEquals(self.newsml.find('TransmissionId').text, '7')
        self.assertEquals(self.newsml.find('DateAndTime').text, '20150613T114519+0000')
        self.assertEquals(self.newsml.find('Priority').get('FormalName'), '1')

    def test_format_identification(self):
        self.formatter._format_identification(self.article, self.newsml)
        self.assertEquals(self.newsml.find('Identification/NewsIdentifier/ProviderId').text, 'sourcefabric.org')
        self.assertEquals(self.newsml.find('Identification/NewsIdentifier/DateId').text, '20150613')
        self.assertEquals(self.newsml.find('Identification/NewsIdentifier/NewsItemId').text, 'urn:localhost.abc')
        self.assertEquals(self.newsml.find('Identification/NewsIdentifier/RevisionId').get('PreviousRevision'), '0')
        self.assertEquals(self.newsml.find('Identification/NewsIdentifier/PublicIdentifier').text, 'urn:localhost.abc')
        self.assertEquals(self.newsml.find('Identification/DateLabel').text, 'Saturday 13 June 2015')

    def test_format_identification_for_corrections(self):
        self.article['state'] = 'corrected'
        self.article['_current_version'] = 7
        self.formatter._format_identification(self.article, self.newsml)
        self.assertEquals(self.newsml.find('Identification/NewsIdentifier/RevisionId').get('PreviousRevision'), '6')
        self.assertEquals(self.newsml.find('Identification/NewsIdentifier/RevisionId').get('Update'), 'A')

    def test_format_news_management(self):
        self.formatter._format_news_management(self.article, self.newsml)
        self.assertEquals(self.newsml.find('NewsManagement/NewsItemType').get('FormalName'), 'News')
        self.assertEquals(self.newsml.find('NewsManagement/FirstCreated').text, '20150613T114519+0000')
        self.assertEquals(self.newsml.find('NewsManagement/ThisRevisionCreated').text, '20150613T114519+0000')
        self.assertEquals(self.newsml.find('NewsManagement/Status').get('FormalName'), 'usable')
        self.assertEquals(self.newsml.find('NewsManagement/Urgency').get('FormalName'), '2')
        self.assertEquals(self.newsml.find('NewsManagement/Instruction').get('FormalName'), 'Update')

    def test_format_news_management_for_corrections(self):
        self.article['state'] = 'corrected'
        self.formatter._format_news_management(self.article, self.newsml)
        self.assertEquals(self.newsml.find('NewsManagement/Instruction').get('FormalName'), 'Correction')

    def test_format_news_component(self):
        with self.app.app_context():
            self.formatter._format_news_component(self.article, self.newsml)
            self.assertEquals(self.newsml.find('NewsComponent/NewsComponent/Role').
                              get('FormalName'), 'Main')
            self.assertEquals(self.newsml.find('NewsComponent/NewsComponent/NewsLines/Headline').
                              text, 'This is a test headline')
            self.assertEquals(self.newsml.find('NewsComponent/NewsComponent/NewsLines/ByLine').
                              text, 'joe')
            self.assertEquals(self.newsml.find('NewsComponent/NewsComponent/NewsLines/DateLine').
                              text, 'sample dateline')
            self.assertEquals(self.newsml.find('NewsComponent/NewsComponent/NewsLines/CreditLine').
                              text, 'sample creditline')
            self.assertEquals(self.newsml.find('NewsComponent/NewsComponent/NewsLines/KeywordLine').
                              text, 'slugline')
            # self.assertEquals(self.newsml.find('NewsComponent/NewsComponent/RightsMetadata/UsageRights/Geography').
            #                   text, 'Australia')
            self.assertEquals(
                self.newsml.findall('NewsComponent/NewsComponent/DescriptiveMetadata/SubjectCode/Subject')[0].
                get('FormalName'), '02011001')
            self.assertEquals(
                self.newsml.findall('NewsComponent/NewsComponent/DescriptiveMetadata/SubjectCode/Subject')[1].
                get('FormalName'), '02011002')
            self.assertEquals(self.newsml.find('NewsComponent/NewsComponent/DescriptiveMetadata/Property').
                              get('Value'), 'a')
            self.assertEquals(
                self.newsml.findall('NewsComponent/NewsComponent/NewsComponent/ContentItem/DataContent')[0].
                text, 'sample abstract')
            self.assertEquals(
                self.newsml.findall('NewsComponent/NewsComponent/NewsComponent/ContentItem/DataContent')[1].
                text, 'The story body')
