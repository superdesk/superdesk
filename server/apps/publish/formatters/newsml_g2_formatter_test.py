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
from apps.publish.formatters.newsml_g2_formatter import NewsMLG2Formatter
import xml.etree.ElementTree as etree
import datetime
from apps.publish import init_app


class NewsMLG2FormatterTest(TestCase):
    article = {
        'guid': 'tag:aap.com.au:20150613:12345',
        '_current_version': 1,
        'anpa_category': [{'qcode': 'a'}],
        'source': 'AAP',
        'headline': 'This is a test headline',
        'byline': 'joe',
        'slugline': 'slugline',
        'subject': [{'qcode': '02011001', 'name': 'international court or tribunal'},
                    {'qcode': '02011002', 'name': 'extradition'}],
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
        self.formatter = NewsMLG2Formatter()
        self.formatter.now = self.now
        self.formatter.string_now = self.now.strftime('%Y-%m-%dT%H:%M:%S.0000Z')
        with self.app.app_context():
            init_app(self.app)
            self.app.data.insert('vocabularies', self.vocab)

    def testFomatter(self):
        with self.app.app_context():
            seq, doc = self.formatter.format(self.article, {'name': 'Test Subscriber'})[0]
            xml = etree.fromstring(doc)
            self.assertEquals(xml.find(
                '{http://iptc.org/std/nar/2006-10-01/}header/{http://iptc.org/std/nar/2006-10-01/}sender').text,
                'sourcefabric.org')
            self.assertEquals(xml.find(
                '{http://iptc.org/std/nar/2006-10-01/}header/{http://iptc.org/std/nar/2006-10-01/}origin').text, 'AAP')
            self.assertEquals(xml.find(
                '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
                '{http://iptc.org/std/nar/2006-10-01/}rightsInfo/{http://iptc.org/std/nar/2006-10-01/}usageTerms').text,
                'terms')
            self.assertEquals(xml.find(
                '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
                '{http://iptc.org/std/nar/2006-10-01/}itemMeta/{http://iptc.org/std/nar/2006-10-01/}provider/' +
                '{http://iptc.org/std/nar/2006-10-01/}name').text,
                'sourcefabric.org')
            self.assertEquals(xml.find(
                '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
                '{http://iptc.org/std/nar/2006-10-01/}contentMeta/{http://iptc.org/std/nar/2006-10-01/}headline').text,
                'This is a test headline')
            self.assertEquals(xml.find(
                '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
                '{http://iptc.org/std/nar/2006-10-01/}contentSet/{http://iptc.org/std/nar/2006-10-01/}inlineXML/' +
                '{http://iptc.org/std/nar/2006-10-01/}nitf/{http://iptc.org/std/nar/2006-10-01/}body/' +
                '{http://iptc.org/std/nar/2006-10-01/}body.content').text, 'The story body')

    def testPreformattedFomatter(self):
        with self.app.app_context():
            article = dict(self.article)
            article['type'] = 'preformatted'
            seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
            xml = etree.fromstring(doc)
            self.assertEquals(xml.find(
                '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
                '{http://iptc.org/std/nar/2006-10-01/}contentSet/{http://iptc.org/std/nar/2006-10-01/}inlineData').text,
                'The story body')

    def testDefaultRightsFomatter(self):
        with self.app.app_context():
            article = dict(self.article)
            article['source'] = 'BOGUS'
            seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
            xml = etree.fromstring(doc)
            self.assertEquals(xml.find(
                '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
                '{http://iptc.org/std/nar/2006-10-01/}rightsInfo/{http://iptc.org/std/nar/2006-10-01/}usageTerms').text,
                'default terms')
