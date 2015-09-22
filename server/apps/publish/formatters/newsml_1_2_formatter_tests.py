# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.utc import utcnow

from test_factory import SuperdeskTestCase
from apps.publish.formatters.newsml_1_2_formatter import NewsML12Formatter
import xml.etree.ElementTree as etree
import datetime
from nose.tools import assert_raises
from superdesk.errors import FormatterError
from apps.publish import init_app


class Newsml12FormatterTest(SuperdeskTestCase):
    article = {
        'source': 'AAP',
        'anpa_category': [{'qcode': 'a', 'name': 'Australian General News'}],
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
        'priority': 1,
        '_current_version': 5,
        '_id': 'urn:localhost.abc',
        'state': 'published',
        'urgency': 2,
        'pubstatus': 'usable',
        'dateline': {
            'source': 'AAP',
            'text': 'sample dateline',
            'located': {
                'alt_name': '',
                'state': 'California',
                'city_code': 'Los Angeles',
                'city': 'Los Angeles',
                'dateline': 'city',
                'country_code': 'US',
                'country': 'USA',
                'tz': 'America/Los_Angeles',
                'state_code': 'CA'
            }
        },
        'keywords': ['traffic'],
        'abstract': 'sample abstract',
        'place': [
            {'qcode': 'NSW', 'name': 'NSW', 'state': 'New South Wales',
             'country': 'Australia', 'world_region': 'Oceania'}
        ],
        'ednote': 'this is test'
    }

    preformatted = {
        'source': 'AAP',
        'anpa_category': [{'qcode': 'a', 'name': 'Australian General News'}],
        'headline': 'This is a test headline',
        'byline': 'joe',
        'slugline': 'slugline',
        'subject': [{'qcode': '02011001'}, {'qcode': '02011002'}],
        'anpa_take_key': 'take_key',
        'unique_id': '1',
        'type': 'preformatted',
        'body_html': 'The story body',
        'type': 'preformatted',
        'word_count': '1',
        '_id': 'urn:localhost.123',
        '_current_version': 5,
        'state': 'published',
        'urgency': 2,
        'pubstatus': 'usable',
        'dateline': {'text': 'sample dateline'},
        'keywords': ['traffic'],
        'abstract': 'sample abstract',
        'place': [
            {'qcode': 'Australia', 'name': 'Australia', 'state': '',
             'country': 'Australia', 'world_region': 'Oceania'}
        ]
    }

    picture = {
        '_id': 'tag:localhost:2015:cf15b059-b997-4e34-a103-85b8d7ea4ba3',
        'firstcreated': '2015-09-20T06:12:57.000Z',
        'versioncreated': '2015-09-20T06:14:11.000Z',
        'dateline': {
            'source': 'AAP',
            'date': '2015-08-14T04:45:53.000Z'
        },
        'renditions': {
            'viewImage': {
                'height': 415,
                'href': 'http://localhost:5000/api/upload/55cd72811d41c828e1773786/raw?_schema=http',
                'media': '55cd72811d41c828e1773786',
                'mimetype': 'image/jpeg',
                'width': 640
            },
            'baseImage': {
                'height': 909,
                'href': 'http://localhost:5000/api/upload/55cd72811d41c828e1773782/raw?_schema=http',
                'media': '55cd72811d41c828e1773782',
                'mimetype': 'image/jpeg',
                'width': 1400
            },
            'thumbnail': {
                'height': 120,
                'href': 'http://localhost:5000/api/upload/55cd72811d41c828e1773784/raw?_schema=http',
                'media': '55cd72811d41c828e1773784',
                'mimetype': 'image/jpeg',
                'width': 184
            },
            'original': {
                'height': 2455,
                'href': 'http://localhost:5000/api/upload/55cd72801d41c828e1773762/raw?_schema=http',
                'media': '55cd72801d41c828e1773762',
                'mimetype': 'image/jpeg',
                'width': 3777
            }
        },
        'state': 'published',
        'anpa_category': [{'qcode': 'a', 'name': 'Australian General News'}],
        'guid': '20150731001161435160',
        'source': 'AAP Image',
        '_current_version': 1,
        'original_source': 'AAP Image/AAP',
        'description': 'Federal Education Minister Christopher Pyne launches his new book NO ARCHIVING',
        'type': 'picture',
        'slugline': 'NUS CHRISTOPHER PYNE PROTEST',
        'headline': 'NUS CHRISTOPHER PYNE PROTEST',
        'pubstatus': 'usable',
        'ednote': '',
        'byline': 'TRACEY NEARMY',
        'filemeta': {
            'yresolution': [
                300,
                1
            ],
            'exposuretime': [
                1,
                200
            ],
            'copyright': '                                                      ',
            'scenecapturetype': 0,
            'sensingmethod': 2,
            'fnumber': [
                14,
                5
            ],
            'flashpixversion': '0100',
            'xresolution': [
                300,
                1
            ],
            'resolutionunit': 2,
            'subsectimedigitized': '20',
            'exposureprogram': 1,
            'subsectimeoriginal': '20',
            'make': 'NIKON CORPORATION',
            'focallengthin35mmfilm': 200,
            'scenetype': 1,
            'exifimageheight': 2455,
            'saturation': 0,
            'colorspace': 1,
            'subjectdistancerange': 0,
            'datetime': '2015:07:31 18:55:37',
            'software': 'Photogene for iPad v4.3',
            'flash': 16,
            'focallength': [
                200,
                1
            ],
            'componentsconfiguration': '\u0001\u0002\u0003\u0000',
            'lightsource': 3,
            'artist': '                                    ',
            'isospeedratings': 2000,
            'whitepoint': [
                313,
                1000
            ],
            'sharpness': 2,
            'exposuremode': 1,
            'meteringmode': 3,
            'compressedbitsperpixel': [
                4,
                1
            ],
            'model': 'NIKON D800E',
            'subsectime': '20',
            'datetimedigitized': '2015:07:31 18:55:37',
            'exifoffset': 406,
            'contrast': 0,
            'whitebalance': 1,
            'exifimagewidth': 3777,
            'datetimeoriginal': '2015:07:31 18:55:37',
            'customrendered': 0,
            'maxaperturevalue': [
                3,
                1
            ],
            'digitalzoomratio': [
                1,
                1
            ],
            'primarychromaticities': [
                16,
                25
            ],
            'length': 8009209,
            'exifversion': '0230',
            'gaincontrol': 2,
            'gamma': [
                11,
                5
            ],
            'filesource': 3
        },
        'language': 'en',
        'mimetype': 'image/jpeg',
        'sign_off': 'mar',
        'unique_id': 573
    }

    video = {
        '_id': 'urn:newsml:localhost:2015-09-20T16:12:57.333001:f3856812-0999-4ed8-b69e-68dcdeb1ed2e',
        'guid': 'tag:localhost:2015:c11e11c4-cdbc-41ef-b939-2b30dd8365fb',
        'language': 'en',
        'family_id': 'urn:newsml:localhost:2015-09-20T16:12:57.333001:f3856812-0999-4ed8-b69e-68dcdeb1ed2e',
        '_current_version': 3,
        'versioncreated': '2015-09-20T06:14:11.000Z',
        'unique_id': 274,
        'renditions': {
            'original': {
                'media': '55fe4e691d41c8cac923ceb2',
                'href': 'http://192.168.220.176:5000/api/upload/55fe4e691d41c8cac923ceb2/raw?_schema=http',
                'mimetype': 'video/mp4'
            }
        },
        'state': 'in_progress',
        'version_creator': '55ee82871d41c86ee1d78c45',
        'sign_off': 'ADM',
        'media': '55fe4e691d41c8cac923ceb2',
        'source': 'AAP',
        'original_source': 'AAP Video/AAP',
        'pubstatus': 'usable',
        'filemeta': {
            'mime_type': 'video/mp4',
            'last_modification': '1904-01-01T00:00:00+00:00',
            'creation_date': '1904-01-01T00:00:00+00:00',
            'height': '270',
            'width': '480',
            'duration': '0:00:10.224000',
            'comment': 'User volume: 100.0%',
            'length': 877869,
            'endian': 'Big endian'
        },
        'event_id': 'tag:localhost:2015:f3ae4441-4721-4987-8265-88d747b6a550',
        'original_creator': '55ee82871d41c86ee1d78c45',
        'expiry': '2016-12-21T14:14:11.000Z',
        'firstcreated': '2015-09-20T06:12:57.000Z',
        '_created': '2015-09-20T06:12:57.000Z',
        'type': 'video',
        'unique_name': '#274',
        'mimetype': 'video/mp4',
        'version': 2,
        'headline': 'test video',
        'description': 'test video',
        'abstract': 'test video',
        'slugline': 'test video keyword',
        'byline': 'test video',
        'subject': [
            {
                'qcode': '01001000',
                'name': 'archaeology',
                'parent': '01000000'
            }
        ],
        'place': [
            {
                'qcode': 'ACT',
                'name': 'ACT'
            }
        ],
        'anpa_category': [
            {
                'qcode': 'a',
                'name': 'Australian General News'
            }
        ]
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
        self.picture['firstcreated'] = self.now
        self.picture['versioncreated'] = self.now
        self.video['firstcreated'] = self.now
        self.video['versioncreated'] = self.now
        self.newsml = etree.Element("NewsML")
        self.formatter = NewsML12Formatter()
        self.formatter.now = self.now
        self.formatter.string_now = self.now.strftime('%Y%m%dT%H%M%S+0000')
        with self.app.app_context():
            init_app(self.app)
            self.app.data.insert('vocabularies', self.vocab)

    def test_newsml_formatter_raises_error(self):
        with assert_raises(FormatterError):
            doc = self.article.copy()
            doc.pop('anpa_category', None)
            self.formatter.format(doc, {'name': 'Test Subscriber'})

    def test_format_news_envelope(self):
        self.formatter._format_news_envelope(self.article, self.newsml, 7)
        self.assertEqual(self.newsml.find('TransmissionId').text, '7')
        self.assertEqual(self.newsml.find('DateAndTime').text, '20150613T114519+0000')
        self.assertEqual(self.newsml.find('Priority').get('FormalName'), '1')
        newsml = etree.Element("NewsML")
        self.formatter._format_news_envelope(self.preformatted, newsml, 7)
        self.assertEqual(newsml.find('Priority').get('FormalName'), '5')

    def test_format_identification(self):
        self.formatter._format_identification(self.article, self.newsml)
        self.assertEqual(self.newsml.find('Identification/NewsIdentifier/ProviderId').text, 'sourcefabric.org')
        self.assertEqual(self.newsml.find('Identification/NewsIdentifier/DateId').text, '20150613')
        self.assertEqual(self.newsml.find('Identification/NewsIdentifier/NewsItemId').text, 'urn:localhost.abc')
        self.assertEqual(self.newsml.find('Identification/NewsIdentifier/RevisionId').get('PreviousRevision'), '0')
        self.assertEqual(self.newsml.find('Identification/NewsIdentifier/PublicIdentifier').text,
                         'urn:localhost.abc:5N')
        self.assertEqual(self.newsml.find('Identification/DateLabel').text, 'Saturday 13 June 2015')

    def test_format_identification_for_corrections(self):
        self.article['state'] = 'corrected'
        self.article['_current_version'] = 7
        self.formatter._format_identification(self.article, self.newsml)
        self.assertEqual(self.newsml.find('Identification/NewsIdentifier/RevisionId').get('PreviousRevision'), '6')
        self.assertEqual(self.newsml.find('Identification/NewsIdentifier/RevisionId').get('Update'), 'N')
        self.article['state'] = 'killed'
        self.formatter._format_identification(self.article, self.newsml)
        self.assertEqual(self.newsml.find('Identification/NewsIdentifier/RevisionId').get('PreviousRevision'), '6')
        self.assertEqual(self.newsml.find('Identification/NewsIdentifier/RevisionId').get('Update'), 'N')

    def test_format_news_management(self):
        self.formatter._format_news_management(self.article, self.newsml)
        self.assertEqual(self.newsml.find('NewsManagement/NewsItemType').get('FormalName'), 'News')
        self.assertEqual(self.newsml.find('NewsManagement/FirstCreated').text, '20150613T114519+0000')
        self.assertEqual(self.newsml.find('NewsManagement/ThisRevisionCreated').text, '20150613T114519+0000')
        self.assertEqual(self.newsml.find('NewsManagement/Status').get('FormalName'), 'usable')
        self.assertEqual(self.newsml.find('NewsManagement/Urgency').get('FormalName'), '2')
        self.assertEqual(self.newsml.find('NewsManagement/Instruction').get('FormalName'), 'Update')

    def test_format_news_management_for_corrections(self):
        self.article['state'] = 'corrected'
        self.formatter._format_news_management(self.article, self.newsml)
        self.assertEqual(self.newsml.find('NewsManagement/Instruction').get('FormalName'), 'Correction')

    def test_format_news_component(self):
        self.formatter._format_news_component(self.article, self.newsml)
        self.assertEqual(self.newsml.find('NewsComponent/NewsComponent/Role').
                         get('FormalName'), 'Main')
        self.assertEqual(self.newsml.find('NewsComponent/NewsComponent/NewsLines/Headline').
                         text, 'This is a test headline')
        self.assertEqual(self.newsml.find('NewsComponent/NewsComponent/NewsLines/ByLine').
                         text, 'joe')
        self.assertEqual(self.newsml.find('NewsComponent/NewsComponent/NewsLines/DateLine').
                         text, 'sample dateline')
        self.assertEqual(self.newsml.find('NewsComponent/NewsComponent/NewsLines/CreditLine').
                         text, 'AAP')
        self.assertEqual(self.newsml.find('NewsComponent/NewsComponent/NewsLines/KeywordLine').
                         text, 'slugline')
        self.assertEqual(
            self.newsml.findall('NewsComponent/NewsComponent/DescriptiveMetadata/SubjectCode/Subject')[0].
            get('FormalName'), '02011001')
        self.assertEqual(
            self.newsml.findall('NewsComponent/NewsComponent/DescriptiveMetadata/SubjectCode/Subject')[1].
            get('FormalName'), '02011002')
        self.assertEqual(self.newsml.find('NewsComponent/NewsComponent/DescriptiveMetadata/Property').
                         get('Value'), 'a')
        self.assertEqual(
            self.newsml.findall('NewsComponent/NewsComponent/NewsComponent/ContentItem/DataContent')[0].
            text, 'sample abstract')
        self.assertEqual(
            self.newsml.findall('NewsComponent/NewsComponent/NewsComponent/ContentItem/DataContent')[1].
            text, 'The story body')
        self.assertEqual(self.newsml.find('.//NewsLines/NewsLine/NewsLineText').text, 'this is test')

    def test_format_news_management_for_embargo(self):
        embargo_ts = (utcnow() + datetime.timedelta(days=2))
        doc = self.article.copy()
        doc['embargo'] = embargo_ts

        self.formatter._format_news_management(doc, self.newsml)

        self.assertEqual(self.newsml.find('NewsManagement/NewsItemType').get('FormalName'), 'News')
        self.assertEqual(self.newsml.find('NewsManagement/FirstCreated').text, '20150613T114519+0000')
        self.assertEqual(self.newsml.find('NewsManagement/ThisRevisionCreated').text, '20150613T114519+0000')
        self.assertEqual(self.newsml.find('NewsManagement/Urgency').get('FormalName'), '2')
        self.assertEqual(self.newsml.find('NewsManagement/Instruction').get('FormalName'), 'Update')
        self.assertEqual(self.newsml.find('NewsManagement/Status').get('FormalName'), 'Embargoed')
        self.assertEqual(self.newsml.find('NewsManagement/StatusWillChange/FutureStatus').get('FormalName'), 'usable')
        self.assertEqual(self.newsml.find('NewsManagement/StatusWillChange/DateAndTime').text, embargo_ts.isoformat())

    def test_format_place(self):
        doc = self.article.copy()
        self.formatter._format_place(doc, self.newsml)
        self.assertEqual(self.newsml.find('Location/Property[@FormalName="CountryArea"]').text, "New South Wales")
        self.assertEqual(self.newsml.find('Location/Property[@FormalName="Country"]').text, "Australia")
        self.assertEqual(self.newsml.find('Location/Property[@FormalName="WorldRegion"]').text, "Oceania")

    def test_format_dateline(self):
        doc = self.article.copy()
        self.formatter._format_dateline(doc, self.newsml)
        self.assertEqual(self.newsml.find('Location/Property[@FormalName="City"]').text, "Los Angeles")
        self.assertEqual(self.newsml.find('Location/Property[@FormalName="CountryArea"]').text, "California")
        self.assertEqual(self.newsml.find('Location/Property[@FormalName="Country"]').text, "USA")

    def test_duration(self):
        self.assertEqual(self.formatter._get_total_duration(None), 0)
        self.assertEqual(self.formatter._get_total_duration('dsf'), 0)
        self.assertEqual(self.formatter._get_total_duration('0:1:0.0000'), 60)
        self.assertEqual(self.formatter._get_total_duration('0:1:10.0000'), 70)
        self.assertEqual(self.formatter._get_total_duration('1:1:10.0000'), 3670)

    def test_format_picture(self):
        doc = self.picture.copy()
        seq, xml_str = self.formatter.format(doc, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(xml_str)

        self.assertEqual(xml.find('NewsItem/NewsComponent/NewsComponent/NewsLines/Headline').text,
                         'NUS CHRISTOPHER PYNE PROTEST')
        self.assertEqual(xml.find('NewsItem/NewsComponent/NewsComponent/NewsLines/ByLine').text, 'TRACEY NEARMY')
        self.assertEqual(xml.find('NewsItem/NewsComponent/NewsComponent/NewsLines/CreditLine').text, 'AAP Image/AAP')
        self.assertEqual(xml.find('NewsItem/NewsComponent/NewsComponent/NewsLines/KeywordLine').text,
                         'NUS CHRISTOPHER PYNE PROTEST')
        self.assertEqual(xml.find(('NewsItem/NewsComponent/NewsComponent/DescriptiveMetadata/'
                                   'Property[@FormalName="Category"]')).get('Value'), 'a')

        for rendition, value in doc.get('renditions').items():
            xpath = './/Role[@FormalName="{}"]/../ContentItem'.format(rendition)
            content_item = xml.find(xpath)
            self.assertEqual(content_item.get('Href'), value.get('href'))
            self.assertEqual(content_item.find('MediaType').get('FormalName'), 'Photo')
            self.assertEqual(content_item.find('Format').get('FormalName'), value.get('mimetype'))
            self.assertEqual(content_item.find('Characteristics/Property[@FormalName="Width"]').get('Value'),
                             str(value.get('width')))
            self.assertEqual(content_item.find('Characteristics/Property[@FormalName="Height"]').get('Value'),
                             str(value.get('height')))

    def test_format_video(self):
        doc = self.video.copy()
        seq, xml_str = self.formatter.format(doc, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(xml_str)
        self.assertEqual(xml.find('NewsItem/NewsComponent/NewsComponent/NewsLines/Headline').text, 'test video')
        self.assertEqual(xml.find('NewsItem/NewsComponent/NewsComponent/NewsLines/ByLine').text, 'test video')
        self.assertEqual(xml.find('NewsItem/NewsComponent/NewsComponent/NewsLines/CreditLine').text, 'AAP Video/AAP')
        self.assertEqual(xml.find('NewsItem/NewsComponent/NewsComponent/NewsLines/KeywordLine').text,
                         'test video keyword')
        for rendition, value in doc.get('renditions').items():
            xpath = './/Role[@FormalName="{}"]/../ContentItem'.format(rendition)
            content_item = xml.find(xpath)
            self.assertEqual(content_item.get('Href'), value.get('href'))
            self.assertEqual(content_item.find('MediaType').get('FormalName'), 'Video')
            self.assertEqual(content_item.find('Format').get('FormalName'), value.get('mimetype'))
            self.assertEqual(content_item.find('Characteristics/Property[@FormalName="Width"]').get('Value'),
                             str(doc.get('filemeta', {}).get('width')))
            self.assertEqual(content_item.find('Characteristics/Property[@FormalName="Height"]').get('Value'),
                             str(doc.get('filemeta', {}).get('height')))
            self.assertEqual(content_item.find('Characteristics/Property[@FormalName="TotalDuration"]').get('Value'),
                             '10')