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
from apps.publish.formatters.ninjs_formatter import NINJSFormatter
from apps.publish import init_app
import json


class ninjsFormatterTest(TestCase):
    def setUp(self):
        super().setUp()
        self.formatter = NINJSFormatter()
        with self.app.app_context():
            init_app(self.app)

    def testTextFomatter(self):
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
            'creditline': 'sample creditline',
            'keywords': ['traffic'],
            'abstract': 'sample abstract',
            'place': 'Australia'
        }
        with self.app.app_context():
            seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
            expected = json.loads(
                '{"version": "1", "place": "Australia", "pubstatus": "usable", \
                "body_html": "The story body", "type": "text", \
                "subject": [{"qcode": "02011001", "name": "international court or tribunal"}, \
                {"qcode": "02011002", "name": "extradition"}], \
                "headline": "This is a test headline", "byline": "joe", "_id": "urn:localhost.abc", "urgency": 2}')
            self.assertEqual(json.loads(doc), expected)

    def testPictureFomatter(self):
        article = {
            '_id': '20150723001158606583',
            '_current_version': 1,
            'slugline': "AMAZING PICTURE",
            'original_source': 'AAP',
            'renditions': {
                'viewImage': {
                    'width': 640,
                    'href': 'http://localhost:5000/api/upload/55b032041d41c8d278d21b6f/raw?_schema=http',
                    'mimetype': 'image/jpeg',
                    "height": 401
                },
                'original_source': {
                    'href': 'https://one-api.aap.com.au/api/v3/Assets/20150723001158606583/Original/download',
                    'mimetype': 'image/jpeg'
                },
            },
            'byline': 'MICKEY MOUSE',
            'headline': 'AMAZING PICTURE',
            'versioncreated': '2015-07-23T00:15:00.000Z',
            'ednote': 'TEST ONLY',
            'type': 'picture',
            'pubstatus': 'usable',
            'source': 'AAP',
            'description': 'The most amazing picture you will ever see',
            'guid': '20150723001158606583'
        }
        with self.app.app_context():
            seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
            expected = json.loads('{"byline": "MICKEY MOUSE", \
                    "renditions": {"viewImage": \
                    {"href": "http://localhost:5000/api/upload/55b032041d41c8d278d21b6f/raw?_schema=http", \
                    "mimetype": "image/jpeg", "width": 640, "height": 401}, \
                    "original_source": {"href": \
                    "https://one-api.aap.com.au/api/v3/Assets/20150723001158606583/Original/download", \
                    "mimetype": "image/jpeg"}}, "headline": "AMAZING PICTURE", "pubstatus": "usable", \
                    "version": "1", "versioncreated": "2015-07-23T00:15:00.000Z", "_id": "20150723001158606583", \
                    "description_text": "The most amazing picture you will ever see", "type": "picture"}')
            self.assertEqual(json.loads(doc), expected)

    def testCompositeFomatter(self):
        article = {
            '_id': 'urn:newsml:localhost:2015-07-24T15:05:00.116047:435c93c2-492c-4668-ab47-ae6e2b9b1c2c',
            'groups': [
                {
                    'id': 'root',
                    'refs': [
                        {
                            'idRef': 'main'
                        },
                        {
                            'idRef': 'sidebars'
                        }
                    ],
                    'role': 'grpRole:NEP'
                },
                {
                    'id': 'main',
                    'refs': [
                        {
                            'renditions': {},
                            'slugline': 'Boat',
                            'guid': 'tag:localhost:2015:515b895a-b336-48b2-a506-5ffaf561b916',
                            'headline': 'WA:Navy steps in with WA asylum-seeker boat',
                            'location': 'archive',
                            'type': 'text',
                            'itemClass': 'icls:text',
                            'residRef': 'tag:localhost:2015:515b895a-b336-48b2-a506-5ffaf561b916'
                        }
                    ],
                    'role': 'grpRole:main'
                },
                {
                    'id': 'sidebars',
                    'refs': [
                        {
                            'renditions': {
                                'original_source': {
                                    'href':
                                        'https://one-api.aap.com.au\
                                        /api/v3/Assets/20150723001158639795/Original/download',
                                    'mimetype': 'image/jpeg'
                                },
                                'original': {
                                    'width': 2784,
                                    'height': 4176,
                                    'href': 'http://localhost:5000\
                                    /api/upload/55b078b21d41c8e974d17ec5/raw?_schema=http',
                                    'mimetype': 'image/jpeg',
                                    'media': '55b078b21d41c8e974d17ec5'
                                },
                                'thumbnail': {
                                    'width': 80,
                                    'height': 120,
                                    'href': 'http://localhost:5000\
                                    /api/upload/55b078b41d41c8e974d17ed3/raw?_schema=http',
                                    'mimetype': 'image/jpeg',
                                    'media': '55b078b41d41c8e974d17ed3'
                                },
                                'viewImage': {
                                    'width': 426,
                                    'height': 640,
                                    'href': 'http://localhost:5000\
                                    /api/upload/55b078b31d41c8e974d17ed1/raw?_schema=http',
                                    'mimetype': 'image/jpeg',
                                    'media': '55b078b31d41c8e974d17ed1'
                                },
                                'baseImage': {
                                    'width': 933,
                                    'height': 1400,
                                    'href': 'http://localhost:5000\
                                    /api/upload/55b078b31d41c8e974d17ecf/raw?_schema=http',
                                    'mimetype': 'image/jpeg',
                                    'media': '55b078b31d41c8e974d17ecf'
                                }
                            },
                            'slugline': 'ABC SHOP CLOSURES',
                            'type': 'picture',
                            'guid':
                                'urn:newsml:localhost:2015-07-24T15:04:29.589984:af3bef9a-5002-492b-a15a-8b460e69b164',
                            'headline': 'ABC SHOP CLOSURES',
                            'location': 'archive',
                            'itemClass': 'icls:picture',
                            'residRef':
                                'urn:newsml:localhost:2015-07-24T15:04:29.589984:af3bef9a-5002-492b-a15a-8b460e69b164'
                        }
                    ],
                    'role': 'grpRole:sidebars'
                }
            ],
            'description': '',
            'operation': 'update',
            'sign_off': 'mar',
            'type': 'composite',
            'pubstatus': 'usable',
            'version_creator': '558379451d41c83ff598a3af',
            'language': 'en',
            'guid': 'urn:newsml:localhost:2015-07-24T15:05:00.116047:435c93c2-492c-4668-ab47-ae6e2b9b1c2c',
            'unique_name': '#145',
            'headline': 'WA:Navy steps in with WA asylum-seeker boat',
            'original_creator': '558379451d41c83ff598a3af',
            'source': 'AAP',
            '_etag': 'b41df79084304219524a092abf07ecba9e1bb2c5',
            'slugline': 'Boat',
            'firstcreated': '2015-07-24T05:05:00.000Z',
            'unique_id': 145,
            'versioncreated': '2015-07-24T05:05:14.000Z',
            '_updated': '2015-07-24T05:05:25.000Z',
            'family_id': 'urn:newsml:localhost:2015-07-24T15:05:00.116047:435c93c2-492c-4668-ab47-ae6e2b9b1c2c',
            '_current_version': 2,
            '_created': '2015-07-24T05:05:00.000Z',
            'version': 2,
        }

        with self.app.app_context():
            seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
            expected = json.loads('{"headline": "WA:Navy steps in with WA asylum-seeker boat", \
            "_created": "2015-07-24T05:05:00.000Z", "version": "2", \
            "_id": "urn:newsml:localhost:2015-07-24T15:05:00.116047:435c93c2-492c-4668-ab47-ae6e2b9b1c2c", \
            "_updated": "2015-07-24T05:05:25.000Z", \
            "associations": {"main": \
            {"_id": "tag:localhost:2015:515b895a-b336-48b2-a506-5ffaf561b916", "type": "text"}, \
            "sidebars": \
            {"_id": "urn:newsml:localhost:2015-07-24T15:04:29.589984:af3bef9a-5002-492b-a15a-8b460e69b164", \
            "type": "picture"}}, "description_text": "", "versioncreated": "2015-07-24T05:05:14.000Z", "type": \
            "composite", "pubstatus": "usable", "language": "en"}')
            self.assertEqual(json.loads(doc), expected)
