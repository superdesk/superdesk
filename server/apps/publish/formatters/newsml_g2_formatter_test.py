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
from apps.publish.formatters.newsml_g2_formatter import NewsMLG2Formatter
import xml.etree.ElementTree as etree
import datetime
from apps.publish import init_app


class NewsMLG2FormatterTest(SuperdeskTestCase):
    embargo_ts = (utcnow() + datetime.timedelta(days=2))
    article = {
        'guid': 'tag:aap.com.au:20150613:12345',
        '_current_version': 1,
        'anpa_category': [
            {
                'qcode': 'a',
                'name': 'Australian General News'
            }
        ],
        'source': 'AAP',
        'headline': 'This is a test headline',
        'byline': 'joe',
        'slugline': 'slugline',
        'subject': [{'qcode': '02011001', 'name': 'international court or tribunal'},
                    {'qcode': '02011002', 'name': 'extradition'}],
        'anpa_take_key': 'take_key',
        'unique_id': '1',
        'body_html': 'The story body',
        'type': 'text',
        'word_count': '1',
        'priority': '1',
        '_id': 'urn:localhost.abc',
        'state': 'published',
        'urgency': 2,
        'pubstatus': 'usable',
        'dateline': {
            'source': 'AAP',
            'text': 'Los Angeles, Aug 11 AAP -',
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
        'creditline': 'sample creditline',
        'keywords': ['traffic'],
        'abstract': 'sample abstract',
        'place': [{'qcode': 'Australia', 'name': 'Australia',
                   'state': '', 'country': 'Australia',
                   'world_region': 'Oceania'}],
        'embargo': embargo_ts
    }

    package = {
        '_id': 'urn:newsml:localhost:2015-08-12T11:59:58.457029:7e90d257-92f6-406d-9186-95653b211701',
        'type': 'composite',
        '_current_version': 1,
        'groups': [
            {
                'role': 'grpRole:NEP',
                'id': 'root',
                'refs': [
                    {
                        'idRef': 'main'
                    }
                ]
            },
            {
                'role': 'grpRole:main',
                'id': 'main',
                'refs': [
                    {
                        'type': 'text',
                        'renditions': {},
                        'itemClass': 'icls:text',
                        'guid': 'tag:localhost:2015:5838657b-b3ec-4e5a-9b39-36039e16400b',
                        'residRef': 'tag:localhost:2015:5838657b-b3ec-4e5a-9b39-36039e16400b',
                        'location': 'archive',
                        'headline': 'US:US cop sacked over student shooting',
                        'slugline': 'US Police'
                    }
                ]
            }
        ],
        'pubstatus': 'usable',
        'state': 'published',
        'marked_for_not_publication': False,
        'guid': 'urn:newsml:localhost:2015-08-12T11:59:58.457029:7e90d257-92f6-406d-9186-95653b211701',
        'dateline': {
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
            },
            'date': '2015-08-12T01:59:58.000Z',
            'source': 'AAP',
            'text': 'Los Angeles, Aug 11 AAP -'
        },
        'language': 'en',
        'headline': 'Cop sacked over student shooting',
        'source': 'AAP',
        'slugline': 'US Police',
        'anpa_category': [
            {
                'name': 'International News',
                'qcode': 'I'
            }
        ],
        'subject': [
            {
                'name': 'police',
                'parent': '02000000',
                'qcode': '02003000'
            }
        ]
    }

    picture_package = {
        '_id': 'urn:newsml:localhost:2015-08-13T14:07:59.846466:c659e21b-1ea2-48b7-9b35-e971ae9d1e6e',
        'guid': 'urn:newsml:localhost:2015-08-13T14:07:59.846466:c659e21b-1ea2-48b7-9b35-e971ae9d1e6e',
        'language': 'en',
        'pubstatus': 'usable',
        'groups': [
            {
                'refs': [
                    {
                        'idRef': 'main'
                    }
                ],
                'id': 'root',
                'role': 'grpRole:NEP'
            },
            {
                'refs': [
                    {
                        'guid': '20150813001165688150',
                        'headline': 'Prison Riot',
                        'residRef': 'tag:localhost:2015:0c12aa0a-82ef-4c58-a363-c5bd8a368037',
                        'location': 'archive',
                        'type': 'picture',
                        'slugline': 'Prison Riot',
                        'renditions': {
                            'baseImage': {
                                'height': 1400,
                                'mimetype': 'image/jpeg',
                                'width': 1120,
                                'href': 'http://localhost:5000/api/upload/55cc03731d41c8cea12b650a/raw?_schema=http',
                                'media': '55cc03731d41c8cea12b650a'
                            },
                            'thumbnail': {
                                'height': 120,
                                'mimetype': 'image/jpeg',
                                'width': 96,
                                'href': 'http://localhost:5000/api/upload/55cc03731d41c8cea12b650c/raw?_schema=http',
                                'media': '55cc03731d41c8cea12b650c'
                            },
                            'viewImage': {
                                'height': 640,
                                'mimetype': 'image/jpeg',
                                'width': 512,
                                'href': 'http://localhost:5000/api/upload/55cc03731d41c8cea12b650e/raw?_schema=http',
                                'media': '55cc03731d41c8cea12b650e'
                            },
                            'original': {
                                'height': 800,
                                'mimetype': 'image/jpeg',
                                'width': 640,
                                'href': 'http://localhost:5000/api/upload/55cc03731d41c8cea12b6508/raw?_schema=http',
                                'media': '55cc03731d41c8cea12b6508'
                            }
                        },
                        'itemClass': 'icls:picture'
                    }
                ],
                'id': 'main',
                'role': 'grpRole:main'
            }
        ],
        'type': 'composite',
        'state': 'published',
        'slugline': 'Prison Riot',
        'description': 'This Jan. 21, 2015 photo is of something)',
        'source': 'AAP',
        'headline': 'Prison Riot',
        '_current_version': 1,
        'dateline': {
            'date': '2015-08-13T04:07:59.000Z',
            'source': 'AAP'
        },
        'marked_for_not_publication': False,
        'sign_off': 'mar',
    }

    picture = {
        '_id': 'tag:localhost:2015:cf15b059-b997-4e34-a103-85b8d7ea4ba3',
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
        'headline': 'test',
        'description': 'testing video',
        'abstract': 'test video',
        'slugline': 'test video',
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

    picture_text_package = {
        '_id': 'urn:newsml:localhost:2015-08-13T14:07:59.846466:c659e21b-1ea2-48b7-9b35-e971ae9d1e6e',
        'guid': 'urn:newsml:localhost:2015-08-13T14:07:59.846466:c659e21b-1ea2-48b7-9b35-e971ae9d1e6e',
        'language': 'en',
        'pubstatus': 'usable',
        'groups': [
            {
                'refs': [
                    {
                        'idRef': 'main'
                    }
                ],
                'id': 'root',
                'role': 'grpRole:NEP'
            },
            {
                'refs': [
                    {
                        'type': 'text',
                        'renditions': {},
                        'itemClass': 'icls:text',
                        'guid': 'tag:localhost:2015:5838657b-b3ec-4e5a-9b39-36039e16400b',
                        'residRef': 'tag:localhost:2015:5838657b-b3ec-4e5a-9b39-36039e16400b',
                        'location': 'archive',
                        'headline': 'US:US cop sacked over student shooting',
                        'slugline': 'US Police',
                        '_current_version': 4
                    },
                    {
                        'guid': '20150813001165688150',
                        'headline': 'Prison Riot',
                        'residRef': 'tag:localhost:2015:0c12aa0a-82ef-4c58-a363-c5bd8a368037',
                        'location': 'archive',
                        'type': 'picture',
                        'slugline': 'Prison Riot',
                        'renditions': {
                            'baseImage': {
                                'height': 1400,
                                'mimetype': 'image/jpeg',
                                'width': 1120,
                                'href': 'http://localhost:5000/api/upload/55cc03731d41c8cea12b650a/raw?_schema=http',
                                'media': '55cc03731d41c8cea12b650a'
                            },
                            'thumbnail': {
                                'height': 120,
                                'mimetype': 'image/jpeg',
                                'width': 96,
                                'href': 'http://localhost:5000/api/upload/55cc03731d41c8cea12b650c/raw?_schema=http',
                                'media': '55cc03731d41c8cea12b650c'
                            },
                            'viewImage': {
                                'height': 640,
                                'mimetype': 'image/jpeg',
                                'width': 512,
                                'href': 'http://localhost:5000/api/upload/55cc03731d41c8cea12b650e/raw?_schema=http',
                                'media': '55cc03731d41c8cea12b650e'
                            },
                            'original': {
                                'height': 800,
                                'mimetype': 'image/jpeg',
                                'width': 640,
                                'href': 'http://localhost:5000/api/upload/55cc03731d41c8cea12b6508/raw?_schema=http',
                                'media': '55cc03731d41c8cea12b6508'
                            }
                        },
                        'itemClass': 'icls:picture',
                        '_current_version': 4
                    }
                ],
                'id': 'main',
                'role': 'grpRole:main'
            }
        ],
        'type': 'composite',
        'state': 'published',
        'slugline': 'Prison Riot',
        'description': 'This Jan. 21, 2015 photo is of something)',
        'source': 'AAP',
        'headline': 'Prison Riot',
        '_current_version': 1,
        'dateline': {
            'date': '2015-08-13T04:07:59.000Z',
            'source': 'AAP'
        },
        'marked_for_not_publication': False,
        'sign_off': 'mar',
    }

    picture_text_package_multi_group = {
        '_id': 'urn:newsml:localhost:2015-08-13T14:07:59.846466:c659e21b-1ea2-48b7-9b35-e971ae9d1e6e',
        'guid': 'urn:newsml:localhost:2015-08-13T14:07:59.846466:c659e21b-1ea2-48b7-9b35-e971ae9d1e6e',
        'language': 'en',
        'pubstatus': 'usable',
        'groups': [
            {
                'refs': [
                    {'idRef': 'main'}, {'idRef': 'picture'}
                ],
                'id': 'root',
                'role': 'grpRole:NEP'
            },
            {
                'refs': [
                    {
                        'type': 'text',
                        'renditions': {},
                        'itemClass': 'icls:text',
                        'guid': 'tag:localhost:2015:5838657b-b3ec-4e5a-9b39-36039e16400b',
                        'residRef': 'tag:localhost:2015:5838657b-b3ec-4e5a-9b39-36039e16400b',
                        'location': 'archive',
                        'headline': 'US:US cop sacked over student shooting',
                        'slugline': 'US Police',
                        '_current_version': 4
                    }
                ],
                'id': 'main',
                'role': 'grpRole:main'
            },
            {
                'refs': [
                    {
                        'guid': '20150813001165688150',
                        'headline': 'Prison Riot',
                        'residRef': 'tag:localhost:2015:0c12aa0a-82ef-4c58-a363-c5bd8a368037',
                        'location': 'archive',
                        'type': 'picture',
                        'slugline': 'Prison Riot',
                        'renditions': {
                            'baseImage': {
                                'height': 1400,
                                'mimetype': 'image/jpeg',
                                'width': 1120,
                                'href': 'http://localhost:5000/api/upload/55cc03731d41c8cea12b650a/raw?_schema=http',
                                'media': '55cc03731d41c8cea12b650a'
                            },
                            'thumbnail': {
                                'height': 120,
                                'mimetype': 'image/jpeg',
                                'width': 96,
                                'href': 'http://localhost:5000/api/upload/55cc03731d41c8cea12b650c/raw?_schema=http',
                                'media': '55cc03731d41c8cea12b650c'
                            },
                            'viewImage': {
                                'height': 640,
                                'mimetype': 'image/jpeg',
                                'width': 512,
                                'href': 'http://localhost:5000/api/upload/55cc03731d41c8cea12b650e/raw?_schema=http',
                                'media': '55cc03731d41c8cea12b650e'
                            },
                            'original': {
                                'height': 800,
                                'mimetype': 'image/jpeg',
                                'width': 640,
                                'href': 'http://localhost:5000/api/upload/55cc03731d41c8cea12b6508/raw?_schema=http',
                                'media': '55cc03731d41c8cea12b6508'
                            }
                        },
                        'itemClass': 'icls:picture',
                        '_current_version': 4
                    }
                ],
                'id': 'picture',
                'role': 'grpRole:picture'
            }
        ],
        'type': 'composite',
        'state': 'published',
        'slugline': 'Prison Riot',
        'description': 'This Jan. 21, 2015 photo is of something)',
        'source': 'AAP',
        'headline': 'Prison Riot',
        '_current_version': 1,
        'dateline': {
            'date': '2015-08-13T04:07:59.000Z',
            'source': 'AAP'
        },
        'marked_for_not_publication': False,
        'sign_off': 'mar',
    }

    packaged_articles = [{'_id': 'tag:localhost:2015:5838657b-b3ec-4e5a-9b39-36039e16400b',
                          'headline': 'package article headline',
                          'slugline': 'slugline',
                          'pubStatus': 'usable'},
                         {'_id': 'tag:localhost:2015:0c12aa0a-82ef-4c58-a363-c5bd8a368037',
                          'headline': 'package article headline',
                          'slugline': 'slugline',
                          'pubStatus': 'usable'}]

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
        init_app(self.app)
        self.app.data.insert('vocabularies', self.vocab)
        self.app.data.insert('archive', self.packaged_articles)

    def testFomatter(self):
        seq, doc = self.formatter.format(self.article, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(doc)
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}header/{http://iptc.org/std/nar/2006-10-01/}sender').text,
            'sourcefabric.org')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}header/{http://iptc.org/std/nar/2006-10-01/}priority').text,
            '1')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}header/{http://iptc.org/std/nar/2006-10-01/}origin').text, 'AAP')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}rightsInfo/{http://iptc.org/std/nar/2006-10-01/}usageTerms').text,
            'terms')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}itemMeta/{http://iptc.org/std/nar/2006-10-01/}provider/' +
            '{http://iptc.org/std/nar/2006-10-01/}name').text,
            'sourcefabric.org')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentMeta/{http://iptc.org/std/nar/2006-10-01/}headline').text,
            'This is a test headline')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentMeta/{http://iptc.org/std/nar/2006-10-01/}urgency').text,
            '2')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentMeta/{http://iptc.org/std/nar/2006-10-01/}dateline').text,
            'Los Angeles, Aug 11 AAP -')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentMeta/' +
            '{http://iptc.org/std/nar/2006-10-01/}located[@qcode="loctyp:City"]/' +
            '{http://iptc.org/std/nar/2006-10-01/}name').text, 'Los Angeles')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentMeta/' +
            '{http://iptc.org/std/nar/2006-10-01/}located/' +
            '{http://iptc.org/std/nar/2006-10-01/}broader[@qcode="loctyp:CountryArea"]/' +
            '{http://iptc.org/std/nar/2006-10-01/}name').text, 'California')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentMeta/' +
            '{http://iptc.org/std/nar/2006-10-01/}located/' +
            '{http://iptc.org/std/nar/2006-10-01/}broader[@qcode="loctyp:Country"]/' +
            '{http://iptc.org/std/nar/2006-10-01/}name').text, 'USA')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentSet/{http://iptc.org/std/nar/2006-10-01/}inlineXML/' +
            '{http://iptc.org/std/nar/2006-10-01/}nitf/{http://iptc.org/std/nar/2006-10-01/}body/' +
            '{http://iptc.org/std/nar/2006-10-01/}body.content').text, 'The story body')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}itemMeta/{http://iptc.org/std/nar/2006-10-01/}embargoed').text,
            self.embargo_ts.isoformat())

    def testPreformattedFomatter(self):
        article = dict(self.article)
        article['type'] = 'preformatted'
        seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(doc)
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentSet/{http://iptc.org/std/nar/2006-10-01/}inlineData').text,
            'The story body')

    def testDefaultRightsFomatter(self):
        article = dict(self.article)
        article['source'] = 'BOGUS'
        seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(doc)
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}rightsInfo/{http://iptc.org/std/nar/2006-10-01/}usageTerms').text,
            'default terms')

    def testPackagePublish(self):
        article = dict(self.package)
        article['firstcreated'] = self.now
        article['versioncreated'] = self.now
        seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(doc)
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}header/{http://iptc.org/std/nar/2006-10-01/}priority').text,
            '5')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}packageItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}groupSet/{http://iptc.org/std/nar/2006-10-01/}group/' +
            '{http://iptc.org/std/nar/2006-10-01/}itemRef/{http://iptc.org/std/nar/2006-10-01/}slugline').text,
            'slugline')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}packageItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}groupSet/{http://iptc.org/std/nar/2006-10-01/}group/' +
            '{http://iptc.org/std/nar/2006-10-01/}itemRef').get('residref'),
            'tag:localhost:2015:5838657b-b3ec-4e5a-9b39-36039e16400b')

    def testPicturePackagePublish(self):
        article = dict(self.picture_package)
        article['firstcreated'] = self.now
        article['versioncreated'] = self.now
        seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(doc)
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}header/{http://iptc.org/std/nar/2006-10-01/}priority').text,
            '5')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}packageItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}groupSet/{http://iptc.org/std/nar/2006-10-01/}group/' +
            '{http://iptc.org/std/nar/2006-10-01/}itemRef/{http://iptc.org/std/nar/2006-10-01/}slugline').text,
            'slugline')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}packageItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}groupSet/{http://iptc.org/std/nar/2006-10-01/}group/' +
            '{http://iptc.org/std/nar/2006-10-01/}itemRef').get('residref'),
            'tag:localhost:2015:0c12aa0a-82ef-4c58-a363-c5bd8a368037')

    def testPicturePublish(self):
        article = dict(self.picture)
        article['firstcreated'] = self.now
        article['versioncreated'] = self.now
        seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(doc)
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}header/{http://iptc.org/std/nar/2006-10-01/}priority').text,
            '5')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentMeta/' +
            '{http://iptc.org/std/nar/2006-10-01/}creditline').text,
            'AAP Image/AAP')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentSet/' +
            '{http://iptc.org/std/nar/2006-10-01/}remoteContent[@rendition="rendition:original"]').get('width'),
            '3777')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentSet/' +
            '{http://iptc.org/std/nar/2006-10-01/}remoteContent[@rendition="rendition:original"]').get('height'),
            '2455')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentSet/' +
            '{http://iptc.org/std/nar/2006-10-01/}remoteContent[@rendition="rendition:original"]').get('contenttype'),
            'image/jpeg')

    def testVideoPublish(self):
        article = dict(self.video)
        article['firstcreated'] = self.now
        article['versioncreated'] = self.now
        seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(doc)
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}header/{http://iptc.org/std/nar/2006-10-01/}priority').text,
            '5')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentMeta/' +
            '{http://iptc.org/std/nar/2006-10-01/}creditline').text,
            'AAP Video/AAP')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentSet/' +
            '{http://iptc.org/std/nar/2006-10-01/}remoteContent[@rendition="rendition:original"]').get('width'),
            '480')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentSet/' +
            '{http://iptc.org/std/nar/2006-10-01/}remoteContent[@rendition="rendition:original"]').get('height'),
            '270')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentSet/' +
            '{http://iptc.org/std/nar/2006-10-01/}remoteContent[@rendition="rendition:original"]').get('duration'),
            '0:00:10.224000')
        self.assertEqual(xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}contentSet/' +
            '{http://iptc.org/std/nar/2006-10-01/}remoteContent[@rendition="rendition:original"]').get('contenttype'),
            'video/mp4')

    def testPictureTextPackage(self):
        article = dict(self.picture_text_package)
        article['firstcreated'] = self.now
        article['versioncreated'] = self.now
        seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(doc)
        item_refs = xml.findall('.//{http://iptc.org/std/nar/2006-10-01/}itemRef')
        self.assertEqual(len(item_refs), 2)
        self.assertEqual(item_refs[0].get('residref'), 'tag:localhost:2015:5838657b-b3ec-4e5a-9b39-36039e16400b')
        self.assertEqual(item_refs[0].find('{http://iptc.org/std/nar/2006-10-01/}itemClass').get('qcode'),
                         'ninat:text')
        self.assertEqual(item_refs[0].find('{http://iptc.org/std/nar/2006-10-01/}pubStatus').get('qcode'),
                         'stat:usable')
        self.assertEqual(item_refs[1].get('residref'), 'tag:localhost:2015:0c12aa0a-82ef-4c58-a363-c5bd8a368037')
        self.assertEqual(item_refs[1].find('{http://iptc.org/std/nar/2006-10-01/}itemClass').get('qcode'),
                         'ninat:picture')
        self.assertEqual(item_refs[1].find('{http://iptc.org/std/nar/2006-10-01/}pubStatus').get('qcode'),
                         'stat:usable')

    def testPictureTextPackageMultiGroup(self):
        article = dict(self.picture_text_package_multi_group)
        article['firstcreated'] = self.now
        article['versioncreated'] = self.now
        seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(doc)
        item_refs = xml.findall('.//{http://iptc.org/std/nar/2006-10-01/}itemRef')
        self.assertEqual(len(item_refs), 2)
        self.assertEqual(item_refs[0].get('residref'), 'tag:localhost:2015:5838657b-b3ec-4e5a-9b39-36039e16400b')
        self.assertEqual(item_refs[0].find('{http://iptc.org/std/nar/2006-10-01/}itemClass').get('qcode'),
                         'ninat:text')
        self.assertEqual(item_refs[0].find('{http://iptc.org/std/nar/2006-10-01/}pubStatus').get('qcode'),
                         'stat:usable')
        self.assertEqual(item_refs[1].get('residref'), 'tag:localhost:2015:0c12aa0a-82ef-4c58-a363-c5bd8a368037')
        self.assertEqual(item_refs[1].find('{http://iptc.org/std/nar/2006-10-01/}itemClass').get('qcode'),
                         'ninat:picture')
        self.assertEqual(item_refs[1].find('{http://iptc.org/std/nar/2006-10-01/}pubStatus').get('qcode'),
                         'stat:usable')
        groups = xml.findall('.//{http://iptc.org/std/nar/2006-10-01/}group')
        self.assertEqual(len(groups), 3)
        self.assertEqual(groups[0].get('id'), 'root')
        self.assertEqual(groups[0].get('role'), 'grpRole:NEP')
        self.assertEqual(groups[1].get('id'), 'main')
        self.assertEqual(groups[1].get('role'), 'grpRole:main')
        self.assertEqual(groups[2].get('id'), 'picture')
        self.assertEqual(groups[2].get('role'), 'grpRole:picture')

        group_ref = xml.findall('.//{http://iptc.org/std/nar/2006-10-01/}groupRef')
        self.assertEqual(len(group_ref), 2)
        self.assertEqual(group_ref[0].get('idref'), 'main')
        self.assertEqual(group_ref[1].get('idref'), 'picture')

    def testPlace(self):
        article = self.article.copy()
        seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(doc)
        content_meta = xml.find('{http://iptc.org/std/nar/2006-10-01/}itemSet'
                                '/{http://iptc.org/std/nar/2006-10-01/}newsItem/'
                                '{http://iptc.org/std/nar/2006-10-01/}contentMeta')
        subject = content_meta.find('{http://iptc.org/std/nar/2006-10-01/}subject[@qcode="loctyp:Country"]')
        self.assertEqual(subject.find('{http://iptc.org/std/nar/2006-10-01/}name').text, "Australia")
        self.assertEqual(subject.find('{http://iptc.org/std/nar/2006-10-01/}broader' +
                                      '[@qcode="loctyp:WorldArea"]/' +
                                      '{http://iptc.org/std/nar/2006-10-01/}name').text, "Oceania")
        self.assertIsNone(content_meta.find('{http://iptc.org/std/nar/2006-10-01/}'
                                            'subject[@qcode="loctyp:CountryArea"]'))
        article['place'] = [{"name": "ACT", "qcode": "ACT",
                             "state": "Australian Capital Territory",
                             "country": "Australia", "world_region": "Oceania"}]
        seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(doc)
        content_meta = xml.find('{http://iptc.org/std/nar/2006-10-01/}itemSet'
                                '/{http://iptc.org/std/nar/2006-10-01/}newsItem/'
                                '{http://iptc.org/std/nar/2006-10-01/}contentMeta')
        subject = content_meta.find('{http://iptc.org/std/nar/2006-10-01/}subject[@qcode="loctyp:CountryArea"]')
        self.assertEqual(subject.find('{http://iptc.org/std/nar/2006-10-01/}name').text,
                         "Australian Capital Territory")
        self.assertEqual(subject.find('{http://iptc.org/std/nar/2006-10-01/}broader' +
                                      '[@qcode="loctyp:Country"]/' +
                                      '{http://iptc.org/std/nar/2006-10-01/}name').text, "Australia")
        self.assertEqual(subject.find('{http://iptc.org/std/nar/2006-10-01/}broader' +
                                      '[@qcode="loctyp:WorldArea"]/' +
                                      '{http://iptc.org/std/nar/2006-10-01/}name').text, "Oceania")

        article['place'] = [{"name": "EUR", "qcode": "EUR",
                             "state": "", "country": "", "world_region": "Europe"}]
        seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(doc)
        content_meta = xml.find('{http://iptc.org/std/nar/2006-10-01/}itemSet'
                                '/{http://iptc.org/std/nar/2006-10-01/}newsItem/'
                                '{http://iptc.org/std/nar/2006-10-01/}contentMeta')
        subject = content_meta.find('{http://iptc.org/std/nar/2006-10-01/}subject[@qcode="loctyp:WorldArea"]')
        self.assertEqual(subject.find('{http://iptc.org/std/nar/2006-10-01/}name').text, "Europe")
        self.assertIsNone(content_meta.find('{http://iptc.org/std/nar/2006-10-01/}'
                                            'subject[@qcode="loctyp:CountryArea"]'))
        self.assertIsNone(content_meta.find('{http://iptc.org/std/nar/2006-10-01/}'
                                            'subject[@qcode="loctyp:Country"]'))
