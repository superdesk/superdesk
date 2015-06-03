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
from apps.publish import init_app
from apps.publish.formatters.newsml_1_2_formatter import NewsML12Formatter
import xml.etree.ElementTree as etree
import datetime


class Newsml12FormatterTest(TestCase):
    output_channel = [{'_id': '1',
                       'name': 'OC1',
                       'description': 'Testing...',
                       'channel_type': 'metadata',
                       'is_active': True,
                       'format': 'newsml12'}]
    article = {
        'originator': 'AAP',
        'anpa-category': {'qcode': 'a'},
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
        'firstcreated': '2015-05-20 09:45:38.000Z',
        'versioncreated': '2015-05-21 19:45:38.000Z',
        'urgency': 2,
        'pubstatus': 'usable',
        'dateline': 'sample dateline',
        'creditline': 'sample creditline',
        'keywords': ['traffic'],
        'abstract': 'sample abstract',
        'place': 'Australia'
    }

    sel_codes = {'1': ['aaa', 'bbb']}

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.app.data.insert('output_channels', self.output_channel)
            init_app(self.app)
            self.article['state'] = 'published'

    def test_format_news_envelope(self):
        newsml = etree.Element("NewsML")
        formatter = NewsML12Formatter()
        formatter.now = datetime.datetime(2015, 6, 13, 11, 45, 19, 0)
        formatter._NewsML12Formatter__format_news_envelope(self.article, newsml, 7)
        self.assertEquals(newsml.find('TransmissionId').text, 7)
        self.assertEquals(newsml.find('DateAndTime').text, '20150613T114519+0000')
        self.assertEquals(newsml.find('Priority').get('FormalName'), '1')

    def test_format_identification(self):
        newsml = etree.Element("NewsML")
        formatter = NewsML12Formatter()
        formatter.now = datetime.datetime(2015, 6, 13, 11, 45, 19, 0)
        formatter._NewsML12Formatter__format_identification(self.article, newsml)
        self.assertEquals(newsml.find('Identification/NewsIdentifier/ProviderId').text, 'aap.com.au')
        self.assertEquals(newsml.find('Identification/NewsIdentifier/DateId').text, '20150613')
        self.assertEquals(newsml.find('Identification/NewsIdentifier/NewsItemId').text, 'urn:localhost.abc')
        self.assertEquals(newsml.find('Identification/NewsIdentifier/RevisionId').get('PreviousRevision'), '0')
        self.assertEquals(newsml.find('Identification/NewsIdentifier/PublicIdentifier').text, 'urn:localhost.abc')
        self.assertEquals(newsml.find('Identification/DateLabel').text, 'Saturday 13 June 2015')

    def test_format_identification_for_corrections(self):
        newsml = etree.Element("NewsML")
        self.article['state'] = 'corrected'
        self.article['_version'] = 7
        formatter = NewsML12Formatter()
        formatter.now = datetime.datetime(2015, 6, 13, 11, 45, 19, 0)
        formatter._NewsML12Formatter__format_identification(self.article, newsml)
        self.assertEquals(newsml.find('Identification/NewsIdentifier/RevisionId').get('PreviousRevision'), '6')
        self.assertEquals(newsml.find('Identification/NewsIdentifier/RevisionId').get('Update'), 'A')

    def test_format_news_management(self):
        newsml = etree.Element("NewsML")
        formatter = NewsML12Formatter()
        formatter.now = datetime.datetime(2015, 6, 13, 11, 45, 19, 0)
        formatter._NewsML12Formatter__format_news_management(self.article, newsml)
        self.assertEquals(newsml.find('NewsManagement/NewsItemType').get('FormalName'), 'News')
        self.assertEquals(newsml.find('NewsManagement/FirstCreated').text, '2015-05-20 09:45:38.000Z')
        self.assertEquals(newsml.find('NewsManagement/ThisRevisionCreated').text, '2015-05-21 19:45:38.000Z')
        self.assertEquals(newsml.find('NewsManagement/Status').get('FormalName'), 'usable')
        self.assertEquals(newsml.find('NewsManagement/Urgency').get('FormalName'), 2)
        self.assertEquals(newsml.find('NewsManagement/Instruction').get('FormalName'), 'Update')

    def test_format_news_management_for_corrections(self):
        newsml = etree.Element("NewsML")
        self.article['state'] = 'corrected'
        formatter = NewsML12Formatter()
        formatter._NewsML12Formatter__format_news_management(self.article, newsml)
        self.assertEquals(newsml.find('NewsManagement/Instruction').get('FormalName'), 'Correction')

    def test_format_news_component(self):
        newsml = etree.Element("NewsML")
        formatter = NewsML12Formatter()
        formatter.now = datetime.datetime(2015, 6, 13, 11, 45, 19, 0)
        formatter._NewsML12Formatter__format_news_component(self.article, newsml)
        self.assertEquals(newsml.find('NewsComponent/NewsComponent/Role').get('FormalName'), 'Main')
        self.assertEquals(newsml.find('NewsComponent/NewsComponent/NewsLines/Headline').text, 'This is a test headline')
        self.assertEquals(newsml.find('NewsComponent/NewsComponent/NewsLines/ByLine').text, 'joe')
        self.assertEquals(newsml.find('NewsComponent/NewsComponent/NewsLines/DateLine').text, 'sample dateline')
        self.assertEquals(newsml.find('NewsComponent/NewsComponent/NewsLines/CreditLine').text, 'sample creditline')
        self.assertEquals(newsml.find('NewsComponent/NewsComponent/NewsLines/KeywordLine').text, 'traffic')
        self.assertEquals(newsml.find('NewsComponent/NewsComponent/RightsMetadata/UsageRights/Geography').
                          text, 'Australia')

        self.assertEquals(newsml.findall('NewsComponent/NewsComponent/DescriptiveMetadata/SubjectCode/Subject')[0].
                          get('FormalName'), '02011001')
        self.assertEquals(newsml.findall('NewsComponent/NewsComponent/DescriptiveMetadata/SubjectCode/Subject')[1].
                          get('FormalName'), '02011002')
        self.assertEquals(newsml.find('NewsComponent/NewsComponent/DescriptiveMetadata/Property').get('Value'), 'a')
        self.assertEquals(newsml.findall('NewsComponent/NewsComponent/NewsComponent/ContentItem/DataContent')[0].
                          text, 'sample abstract')
        self.assertEquals(newsml.findall('NewsComponent/NewsComponent/NewsComponent/ContentItem/DataContent')[1].
                          text, 'The story body')
