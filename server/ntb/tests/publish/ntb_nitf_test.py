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


@mock.patch('superdesk.publish.subscribers.SubscribersService.generate_sequence_number', lambda self, subscriber: 1)
class NTBNITFFormatterTest(TestCase):
    def setUp(self):
        super().setUp()
        self.formatter = NTBNITFFormatter()
        self.base_formatter = Formatter()
        init_app(self.app)
        self.article = {
            'headline': 'test headline',
            "body_html": "<p class=\"lead\" lede=\"true\">United Nations, United States, July 15, 2016 (AFP) - "
                         "A new round of talks to end the war in Yemen has been delayed by a day and is now exp"
                         "ected to start on Saturday, the UN spokesman said.</p><p class=\"txt\">The talks were"
                         " pushed back while UN envoy Ismail Ould Cheikh Ahmed was in Riyadh to try to persuade"
                         " Yemen's President Abedrabbo Mansour Hadi to come to the negotiating table.</p><p cla"
                         "ss=\"txt-ind\">Negotiators from the Huthi rebels and former president Ali Abdullah Sa"
                         "leh's political party were already in Kuwait awaiting the arrival of the government d"
                         "elegation.</p><p class=\"txt-ind\">\"We will see whether we can get both delegations "
                         "so that we can get the talks started,\" UN spokesman Farhan Haq said on Friday.</p><p"
                         " class=\"txt-ind\">\"If there is any further delay, we can let you know at that time,"
                         " but right now what we are anticipating is a start tomorrow,\" he added.</p><p class="
                         "\"txt-ind\">Yemen's president on Sunday warned that his government would boycott the "
                         "talks if the UN envoy insists on a peace deal that would provide for a unity governme"
                         "nt that includes the insurgents.</p><p class=\"txt-ind\">Hadi accused the Iran-backed"
                         " Huthis of trying to \"legitimize their coup d'etat\" and warned he would not allow Y"
                         "emen to be \"turned into a Persian state.\"</p><p class=\"txt-ind\">More than 6,400 p"
                         "eople have died in Yemen since a Saudi-led coalition intervened in support of Hadi's "
                         "government in March last year.</p><p class=\"txt-ind\">The coalition launched an air "
                         "campaign to push back Huthi rebels after they seized the capital Sanaa and many other"
                         " parts of the country.</p><p class=\"txt-ind\">There has been growing international a"
                         "larm over the heavy civilian toll in Yemen, where 80 percent of the population is in "
                         "urgent need of humanitarian aid.</p><p class=\"txt-ind\">cml/grf</p>\n<!-- EMBED STAR"
                         "T Image {id: \"embedded18237840351\"} -->\n<figure><img src=\"http://scanpix.no/spWeb"
                         "App/previewimage/sdl/preview/tb42bf43.jpg\" alt=\"New parliament speaker Ana Pastor s"
                         "peaks on her phone during the first session of parliament following a general electio"
                         "n in Madrid, Spain, July 19, 2016. REUTERS/Andrea Comas\" /><figcaption>New parliamen"
                         "t speaker Ana Pastor speaks on her phone during the first session of parliament follo"
                         "wing a general election in Madrid, Spain, July 19, 2016. REUTERS/Andrea Comas</figcap"
                         "tion></figure>\n<!-- EMBED END Image {id: \"embedded18237840351\"} -->\n<!-- EMBED ST"
                         "ART Video {id: \"embedded10005446043\"} -->\n<figure><video controls=\"controls\"></v"
                         "ideo><figcaption>\n\nSCRIPT TO FOLLOW\n</figcaption></figure>\n<!-- EMBED END Video {"
                         "id: \"embedded10005446043\"} -->",
            'type': 'text',
            'priority': '2',
            '_id': 'urn:localhost.abc',
            "slugline": "this is the slugline",
            'urgency': 2,
            'subject': [{
                         "scheme": "category",
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
                                        "title": "Scanpix(desk)"
                                    }
                                },
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
                                        "title": "Scanpix(desk)"
                                    }
                                },
                    "headline": "New parliament speaker Ana Pastor speaks on her phone during the first session o"
                                "f parliament following a general election in Madrid"
                },
                "embedded03": None,
            },
        }

    def test_subject_and_category(self):
        seq, doc = self.formatter.format(self.article, {'name': 'Test NTBNITF'})[0]
        nitf_xml = etree.fromstring(doc)
        tobject = nitf_xml.find('head/tobject')
        self.assertEqual(tobject.get('tobject.type'), 'Forskning')
        subject = tobject.find('tobject.subject')
        self.assertEqual(subject.get('tobject.subject.refnum'), '02001003')
        self.assertEqual(subject.get('tobject.subject.type'), 'tyveri og innbrudd')

    def test_priority(self):
        seq, doc = self.formatter.format(self.article, {'name': 'Test NTBNITF'})[0]
        nitf_xml = etree.fromstring(doc)
        priority = nitf_xml.find("head/meta[@name='NTBPrioritet']")
        self.assertEqual(priority.get('content'), '2')

    def test_slugline(self):
        seq, doc = self.formatter.format(self.article, {'name': 'Test NTBNITF'})[0]
        nitf_xml = etree.fromstring(doc)
        du_key = nitf_xml.find('head/docdata/du-key')
        self.assertEqual(du_key.get('key'), 'this is the slugline')

    def test_body(self):
        seq, doc = self.formatter.format(self.article, {'name': 'Test NTBNITF'})[0]
        nitf_xml = etree.fromstring(doc)
        medias = nitf_xml.findall("body/body.content/media")
        image = medias[0]
        self.assertEqual(image.get("media_type"), "image")
        self.assertEqual(image.find("media-reference").get("source"), "tb42bf43")
        self.assertEqual(image.find("media-caption").text,
                         "New parliament speaker Ana Pastor speaks on her phone during the first session of parliament"
                         " following a general election in Madrid, Spain, July 19, 2016. REUTERS/Andrea Comas")
        video = medias[1]
        self.assertEqual(video.get("media_type"), "video")
        self.assertEqual(video.find("media-reference").get("mime-type"), "video/mpeg")
        self.assertEqual(video.find("media-reference").get("source"), "tb42bf38")
        self.assertEqual(video.find("media-caption").text, "\n\nSCRIPT TO FOLLOW\n")
