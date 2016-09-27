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
from ntb.publish.ntb_nitf import ENCODING
from superdesk.publish.formatters import Formatter
from superdesk.publish.subscribers import SubscribersService
from superdesk.publish import init_app
import xml.etree.ElementTree as etree
import datetime
import uuid
import pytz
import copy

TEST_ABSTRACT = "This is the abstract"
TEST_NOT_LEAD = "This should not be lead"
ITEM_ID = str(uuid.uuid4())
NOW = datetime.datetime.now(datetime.timezone.utc)
TEST_BODY = """
<p class="lead" lede="true">""" + TEST_NOT_LEAD + """</p>
<p class="txt">line 1</p>
<p class="txt-ind">line 2</p>
<p class="txt-ind">line 3</p>
<p class="txt-ind">test encoding: –</p>
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
ARTICLE = {
    'headline': 'test headline',
    'abstract': TEST_ABSTRACT,
    'body_html': TEST_BODY,
    'type': 'text',
    'priority': '2',
    '_id': 'urn:localhost.abc',
    'item_id': ITEM_ID,
    "slugline": "this is the slugline",
    'urgency': 2,
    'versioncreated': NOW,
    '_current_version': 2,
    'version': 2,
    'language': 'nb-NO',
    # if you change place, please keep a test with 'parent': None
    # cf SDNTB-290
    'place': [{'scheme': 'place_custom', 'parent': None, 'name': 'Global', 'qcode': 'Global'}],
    'dateline': {
        'located': {
            'dateline': 'city',
            'tz': 'Europe/Oslo',
            'city': 'Hammerfest',
            'state': 'Finnmark',
            'alt_name': '',
            'country': 'Norway',
            'state_code': 'NO.20',
            'country_code': 'NO',
            'city_code': 'Hammerfest'},
        'source': 'NTB',
        'text': 'HAMMERFEST, Sep 13  -'},
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
            "versioncreated": NOW,
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
            "versioncreated": NOW,
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
            "versioncreated": NOW,
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


class NTBNITFFormatterTest(TestCase):

    def __init__(self, *args, **kwargs):
        super(NTBNITFFormatterTest, self).__init__(*args, **kwargs)
        self.article = None

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def setUp(self):
        super().setUp()
        self.formatter = NTBNITFFormatter()
        self.base_formatter = Formatter()
        init_app(self.app)
        self.tz = pytz.timezone(self.app.config['DEFAULT_TIMEZONE'])
        if self.article is None:
            # formatting is done once for all tests to save time
            # as long as used attributes are not modified, it's fine
            self.article = ARTICLE
            self.formatter_output = self.formatter.format(self.article, {'name': 'Test NTBNITF'})
            self.doc = self.formatter_output[0]['formatted_item']
            self.nitf_xml = etree.fromstring(self.doc)

    def test_subject_and_category(self):
        tobject = self.nitf_xml.find('head/tobject')
        self.assertEqual(tobject.get('tobject.type'), 'Forskning')
        subject = tobject.find('tobject.subject')
        self.assertEqual(subject.get('tobject.subject.refnum'), '02001003')
        self.assertEqual(subject.get('tobject.subject.matter'), 'tyveri og innbrudd')

    def test_slugline(self):
        du_key = self.nitf_xml.find('head/docdata/du-key')
        self.assertEqual(du_key.get('key'), 'this is the slugline')

    def test_pubdata(self):
        pubdata = self.nitf_xml.find('head/pubdata')
        expected = NOW.astimezone(self.tz).strftime("%Y%m%dT%H%M%S")
        self.assertEqual(pubdata.get('date.publication'), expected)

    def test_dateline(self):
        dateline = self.nitf_xml.find('body/body.head/dateline')
        self.assertEqual(dateline.text, 'Hammerfest')

    def test_body(self):
        # body content

        body_content = self.nitf_xml.find("body/body.content")
        p_elems = iter(body_content.findall('p'))
        lead = next(p_elems)
        self.assertEqual(lead.get("class"), "lead")
        self.assertEqual(lead.text, TEST_ABSTRACT)
        not_lead = next(p_elems)
        self.assertEqual(not_lead.get("class"), "txt")
        self.assertEqual(not_lead.text, TEST_NOT_LEAD)

        p_lead = body_content.findall('p[@class="lead"]')
        self.assertEqual(len(p_lead), 1)

        for i in range(1, 4):
            p = next(p_elems)
            self.assertEqual(p.text, "line {}".format(i))

        p_encoding = next(p_elems)
        self.assertEqual(p_encoding.text, "test encoding: –")

        hl2 = next(p_elems).find('hl2')
        self.assertEqual(hl2.text, "intermediate line")

        # all embedded must be removed from body's HTML,
        # they are put in <media/> elements
        self.assertNotIn(b'EMBED', etree.tostring(body_content))

        # medias

        medias = body_content.findall("media")
        feature = medias[0]
        self.assertEqual(feature.get("media-type"), "image")
        self.assertEqual(feature.find("media-reference").get("source"), "test_id")
        self.assertEqual(feature.find("media-caption").text, "test feature media")

        image = medias[1]
        self.assertEqual(image.get("media-type"), "image")
        self.assertEqual(image.find("media-reference").get("source"), "tb42bf43")
        self.assertEqual(image.find("media-caption").text,
                         "New parliament speaker Ana Pastor speaks on her phone during the first session of parliament"
                         " following a general election in Madrid, Spain, July 19, 2016. REUTERS/Andrea Comas")
        video = medias[2]
        self.assertEqual(video.get("media-type"), "video")
        self.assertEqual(video.find("media-reference").get("mime-type"), "video/mpeg")
        self.assertEqual(video.find("media-reference").get("source"), "tb42bf38")
        self.assertEqual(video.find("media-caption").text, "\n\nSCRIPT TO FOLLOW\n")

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def test_empty_dateline(self):
        """SDNTB-293 regression test"""
        article = copy.deepcopy(self.article)
        article['dateline'] = {'located': None}
        formatter_output = self.formatter.format(article, {'name': 'Test NTBNITF'})
        doc = formatter_output[0]['formatted_item']
        nitf_xml = etree.fromstring(doc)
        self.assertEqual(nitf_xml.find('body/body.head/dateline'), None)

    def test_encoding(self):
        encoded = self.formatter_output[0]['encoded_item']
        manually_encoded = self.doc.replace('–', '&#8211;').encode(ENCODING)
        self.assertEqual(encoded, manually_encoded)
        formatted = self.doc
        header = formatted[:formatted.find('>') + 1]
        self.assertIn('encoding="{}"'.format(ENCODING), header)

    def test_place(self):
        evloc = self.nitf_xml.find('head/docdata/evloc')
        self.assertEqual(evloc.get('county-dist'), "Global")

    def test_meta(self):
        head = self.nitf_xml.find('head')

        media_counter = head.find('meta[@name="NTBBilderAntall"]')
        self.assertEqual(media_counter.get('content'), '3')
        editor = head.find('meta[@name="NTBEditor"]')
        self.assertEqual(editor.get('content'), 'Superdesk')
        kode = head.find('meta[@name="NTBDistribusjonsKode"]')
        self.assertEqual(kode.get('content'), 'ALL')
        kanal = head.find('meta[@name="NTBKanal"]')
        self.assertEqual(kanal.get('content'), 'A')
        ntb_id = head.find('meta[@name="NTBID"]')
        self.assertEqual(ntb_id.get('content'), 'NTB' + ITEM_ID)
