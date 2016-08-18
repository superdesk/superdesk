# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.tests import TestCase
from unittest import mock
from ntb.publish.ntb_nitf import NTBNITFFormatter
from superdesk.publish.formatters import Formatter
from superdesk.publish import init_app
import xml.etree.ElementTree as etree

TEST_BODY = """
<p class="lead" lede="true">test lead</p>
<p class="txt">line 1</p>
<p class="txt-ind">line 2</p>
<p class="txt-ind">line 3</p>
<!-- EMBED START Image {id: "embedded18237840351"} --><figure>
<img src="http://scanpix.no/spWebApp/previewimage/sdl/preview/tb42bf43.jpg" alt="alt text" />
<figcaption>New parliament speaker Ana Pastor speaks on her phone during the first session of parliament\
following a general election in Madrid, Spain, July 19, 2016. REUTERS/Andrea Comas</figcaption>
</figure><!-- EMBED END Image {id: "embedded18237840351"} -->
<p><h3>intermediate line</h3></p>
<!-- EMBED START Video {id: "embedded10005446043"} --><figure>
<video controls="controls">
</video>
<figcaption>SCRIPT TO FOLLOW</figcaption>
</figure><!-- EMBED END Video {id: "embedded10005446043"} -->
"""


@mock.patch('superdesk.publish.subscribers.SubscribersService.generate_sequence_number', lambda self, subscriber: 1)
class NTBNITFFormatterTest(TestCase):
    def setUp(self):
        super().setUp()
        self.formatter = NTBNITFFormatter()
        self.base_formatter = Formatter()
        init_app(self.app)
        self.article = {
            'headline': 'test headline',
            "body_html": TEST_BODY,
            'type': 'text',
            'priority': '2',
            '_id': 'urn:localhost.abc',
            "slugline": "this is the slugline",
            'urgency': 2,
            'subject': [
                {"scheme": "category",
                 "qcode": "Forskning",
                 "service": {
                     "f": 1,
                     "i": 1},
                 "name": "Forskning"},
                {"scheme": "subject_custom",
                 "qcode": "02001003",
                 "parent": "02000000",
                 "name": "tyveri og innbrudd"}],
            "associations": {

                "featuremedia": {
                    "_id": "test_id",
                    "guid": "test_id",
                    "headline": "feature headline",
                    "ingest_provider": "fdsfdsfsdfs",
                    "original_source": "feature_source",
                    "pubstatus": "usable",
                    "renditions": {
                        "baseImage": {
                            "href": "http://scanpix.no/spWebApp/previewimage/sdl/preview_big/test_id.jpg"
                        },
                        "thumbnail": {
                            "href": "http://preview.scanpix.no/thumbs/tb/4/33/test_id.jpg"
                        },
                        "viewImage": {
                            "href": "http://scanpix.no/spWebApp/previewimage/sdl/preview/test_id.jpg"
                        }},
                    "source": "feature_source",
                    "fetch_endpoint": "scanpix",
                    "type": "picture",
                    "versioncreated": "2016-07-20T07:11:37+0000",
                    "description_text": "test feature media"
                },

                "embedded01": None,
                "embedded10005446043": {
                    "firstcreated": "2016-07-19T16:23:11+0000",
                    "original_source": "Reuters DV",
                    "_updated": "1970-01-01T00:00:00+0000",
                                "mimetype": "video/mpeg",
                                "renditions": {
                                    "viewImage": {
                                        "href": "http://scanpix.no/spWebApp/previewimage/sdl/preview/tb42bf38.jpg"
                                    },
                                    "baseImage": {
                                        "href": "http://scanpix.no/spWebApp/previewimage/sdl/preview/tb42bf38.jpg"
                                    },
                                    "thumbnail": {
                                        "href": "http://preview.scanpix.no/thumbs/tb/4/2b/tb42bf38.jpg"
                                    }
                                },
                    "_etag": "85294f12036b2bb9f97cb9e421961dd330cd1d3d",
                    "pubstatus": "usable",
                    "source": "Reuters DV",
                    "versioncreated": "2016-07-19T14:25:57+0000",
                    "_created": "1970-01-01T00:00:00+0000",
                    "byline": None,
                    "fetch_endpoint": "scanpix",
                    "type": "video",
                    "guid": "tb42bf38",
                    "_id": "tb42bf38",
                    "description_text": "\n\nSCRIPT TO FOLLOW\n",
                    "_type": "externalsource",
                    "ingest_provider": "577148e1cc3a2d5ab90f5d9c",
                    "_links": {
                        "self": {
                            "href": "scanpix(desk)/tb42bf38",
                            "title": "Scanpix(desk)"}},
                    "headline": "Hollande meets Portugal president"
                },
                "embedded18237840351": {
                    "firstcreated": "2016-07-19T16:23:17+0000",
                    "original_source": "Reuters",
                    "_updated": "1970-01-01T00:00:00+0000",
                                "renditions": {
                                    "viewImage": {
                                        "href": "http://scanpix.no/spWebApp/previewimage/sdl/preview/tb42bf43.jpg"
                                    },
                                    "baseImage": {
                                        "href": "http://scanpix.no/spWebApp/previewimage/sdl/preview_big/tb42bf43.jpg"
                                    },
                                    "thumbnail": {
                                        "href": "http://preview.scanpix.no/thumbs/tb/4/2b/tb42bf43.jpg"
                                    }
                                },
                    "pubstatus": "usable",
                    "_etag": "238529c614736dc314165bca1f0da523b82a2d2a",
                    "source": "Reuters",
                    "versioncreated": "2016-07-19T14:25:57+0000",
                    "_created": "1970-01-01T00:00:00+0000",
                    "byline": "Andrea Comas",
                    "fetch_endpoint": "scanpix",
                    "type": "picture",
                    "guid": "tb42bf43",
                    "_id": "tb42bf43",
                    "description_text": "New parliament speaker Ana Pastor speaks on her"
                    " phone during the first "
                    "session of parliament following a general election in Madrid, Spain,"
                    " July 19, 2016. REUTERS/Andrea Comas",
                    "_type": "externalsource",
                    "ingest_provider": "577148e1cc3a2d5ab90f5d9c",
                    "_links": {
                        "self": {
                            "href": "scanpix(desk)/tb42bf43",
                            "title": "Scanpix(desk)"}},
                    "headline": "New parliament speaker Ana Pastor speaks on her phone during the first session o"
                                "f parliament following a general election in Madrid"
                },
                "embedded03": None,
            },
        }

    def test_subject_and_category(self):
        doc = self.formatter.format(self.article, {'name': 'Test NTBNITF'})[0]['formatted_item']
        nitf_xml = etree.fromstring(doc)
        tobject = nitf_xml.find('head/tobject')
        self.assertEqual(tobject.get('tobject.type'), 'Forskning')
        subject = tobject.find('tobject.subject')
        self.assertEqual(subject.get('tobject.subject.refnum'), '02001003')
        self.assertEqual(subject.get('tobject.subject.type'), 'tyveri og innbrudd')

    def test_priority(self):
        doc = self.formatter.format(self.article, {'name': 'Test NTBNITF'})[0]['formatted_item']
        nitf_xml = etree.fromstring(doc)
        priority = nitf_xml.find("head/meta[@name='NTBPrioritet']")
        self.assertEqual(priority.get('content'), '2')

    def test_slugline(self):
        doc = self.formatter.format(self.article, {'name': 'Test NTBNITF'})[0]['formatted_item']
        nitf_xml = etree.fromstring(doc)
        du_key = nitf_xml.find('head/docdata/du-key')
        self.assertEqual(du_key.get('key'), 'this is the slugline')

    def test_body(self):
        doc = self.formatter.format(self.article, {'name': 'Test NTBNITF'})[0]['formatted_item']
        nitf_xml = etree.fromstring(doc)

        # body content

        body_content = nitf_xml.find("body/body.content")
        p_elems = iter(body_content.findall('p'))
        lead = next(p_elems)
        self.assertEqual(lead.get("class"), "lead")
        self.assertEqual(lead.text, "test lead")

        for i in range(1, 4):
            p = next(p_elems)
            self.assertEqual(p.text, "line {}".format(i))

        h3 = next(p_elems).find('h3')
        self.assertEqual(h3.text, "intermediate line")

        # all embedded must be removed from body's HTML,
        # they are put in <media/> elements
        self.assertNotIn(b'EMBED', etree.tostring(body_content))

        # medias

        medias = body_content.findall("media")
        feature = medias[0]
        self.assertEqual(feature.get("media_type"), "image")
        self.assertEqual(feature.find("media-reference").get("source"), "test_id")
        self.assertEqual(feature.find("media-caption").text, "test feature media")

        image = medias[1]
        self.assertEqual(image.get("media_type"), "image")
        self.assertEqual(image.find("media-reference").get("source"), "tb42bf43")
        self.assertEqual(image.find("media-caption").text,
                         "New parliament speaker Ana Pastor speaks on her phone during the first session of parliament"
                         " following a general election in Madrid, Spain, July 19, 2016. REUTERS/Andrea Comas")
        video = medias[2]
        self.assertEqual(video.get("media_type"), "video")
        self.assertEqual(video.find("media-reference").get("mime-type"), "video/mpeg")
        self.assertEqual(video.find("media-reference").get("source"), "tb42bf38")
        self.assertEqual(video.find("media-caption").text, "\n\nSCRIPT TO FOLLOW\n")

    def test_encoding(self):
        doc = self.formatter.format(self.article, {'name': 'Test NTBNITF'})[0]
        encoding = doc['item_encoding']
        self.assertEqual(encoding, 'iso-8859-1')
        formatted = doc['formatted_item']
        header = formatted[:formatted.find('>') + 1]
        self.assertIn('encoding="iso-8859-1"', header)
