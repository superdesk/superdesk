
import io

from lxml import etree
from unittest import mock
from urllib.parse import urlparse

from superdesk.utc import utcnow
from superdesk.tests import TestCase
from .ansa_newsml_g2_formatter import ANSANewsMLG2Formatter

geoname = {
    "region": "Arezzo",
    "scheme": "geonames",
    "state": "Tuscany",
    "state_code": "16",
    "code": "6541097",
    "continent_code": "EU",
    "name": "Monte San Savino",
    "feature_class": "A",
    "region_code": "AR",
    "location": {
        "lat": 43.32924,
        "lon": 11.72974
    },
    "country_code": "IT",
    "country": "Italy"
}


def ns(value):
    return '{http://iptc.org/std/nar/2006-10-01/}%s' % value


def get_content_meta(xml):
    return xml.find('/'.join([ns('itemSet'), ns('newsItem'), ns('contentMeta')]))


@mock.patch('superdesk.publish.subscribers.SubscribersService.generate_sequence_number', lambda self, subscriber: 1)
class ANSANewsmlG2FormatterTestCase(TestCase):
    formatter = ANSANewsMLG2Formatter()

    article = {
        '_id': 'tag:aap.com.au:20150613:12345',
        'guid': 'tag:aap.com.au:20150613:12345',
        '_current_version': 1,
        'anpa_category': [
            {
                'qcode': 'a',
                'name': 'Australian General News'
            }
        ],
        'language': 'en',
        'source': 'AAP',
        'headline': 'This is a test headline',
        'byline': 'joe',
        'slugline': 'slugline',
        'subject': [
            {'qcode': '02011001', 'name': 'international court or tribunal'},
            {'qcode': '02011002', 'name': 'extradition'},
            {'qcode': '020002007289230000', 'name': 'PHOTOMED', 'output_code': 'TECN', 'scheme': 'products'},
        ],
        'anpa_take_key': 'take_key',
        'unique_id': '1',
        'body_html': '<p>The story body <b>HTML</b></p><p>another paragraph</p><style></style>',
        'type': 'text',
        'word_count': '1',
        'priority': '1',
        'state': 'published',
        'urgency': 2,
        'pubstatus': 'usable',
        'dateline': {
            'source': 'ANSA',
            'text': 'Roma (foo), Aug 01 ANSA -',
            'date': '2018-08-01T09:25:19+0000',
            'located': {
                'alt_name': '',
                'state': 'Latium',
                'city_code': 'Rome',
                'city': 'Roma',
                'dateline': 'city',
                'country_code': 'IT',
                'country': 'Italy',
                'tz': 'Europe/Rome',
                'state_code': 'IT.07'
            }
        },
        'creditline': 'sample creditline',
        'copyrightholder': 'FOO',
        'copyrightnotice': 'FOO 2018',
        'keywords': ['traffic'],
        'abstract': 'sample abstract',
        'place': [
            {
                'qcode': 'Australia',
                'name': 'Australia',
                'state': '',
                'country': 'Australia',
                'world_region': 'Oceania',
            },
            {
                'name': 'Roma',
                'qcode': 'n:Roma',
            },
        ],
        'company_codes': [{'name': 'YANCOAL AUSTRALIA LIMITED', 'qcode': 'YAL', 'security_exchange': 'ASX'}],
        'sign_off': 'Foo',
        'extra': {
            'subtitle': '<p>Subtitle text</p>',
            'shorttitle': '<p>Short headline</p>',
            'HeadingNews': '(ANSA)',
        },
        'sms_message': 'SMS message',
        'genre': [{
            'name': "Article (news)",
            'qcode': "Article",
        }],
    }

    vocab = [{'_id': 'rightsinfo', 'items': [{'name': 'AAP',
                                              'copyrightHolder': 'copy right holder',
                                              'copyrightNotice': 'copy right notice',
                                              'usageTerms': 'terms'},
                                             {'name': 'default',
                                              'copyrightHolder': 'default copy right holder',
                                              'copyrightNotice': 'default copy right notice',
                                              'usageTerms': 'default terms'}]}]

    subscriber = {'_id': 'foo', 'name': 'Foo', 'config': {}, 'destinations': []}

    def setUp(self):
        self.app.data.insert('vocabularies', self.vocab)

    def get_article(self, updates=None):
        article = self.article.copy()
        article['firstcreated'] = article['versioncreated'] = utcnow()
        if updates:
            article.update(updates)
        return article

    def test_html_content(self):
        article = self.get_article()
        formatter = ANSANewsMLG2Formatter()
        _, doc = formatter.format(article, self.subscriber)[0]
        self.assertIn('<body>', doc)
        self.assertIn('<b>HTML</b>', doc)

    def test_html_empty_content(self):
        article = self.get_article()
        article['body_html'] = ''
        formatter = ANSANewsMLG2Formatter()
        _, doc = formatter.format(article, self.subscriber)[0]
        self.assertIn('<body>', doc)

    def test_featured_item_link(self):
        media = self.app.media.put(io.BytesIO(b'test'))
        article = self.get_article()
        article['associations'] = {
            'featuremedia': {
                'type': 'picture',
                'renditions': {
                    'original': {
                        'mimetype': 'image/jpeg',
                        'media': media,
                    }
                }
            }
        }

        formatter = ANSANewsMLG2Formatter()
        _, doc = formatter.format(article, self.subscriber)[0]
        self.assertIn('<link', doc)
        xml = etree.fromstring(doc.encode('utf-8'))
        link = xml.find('/'.join([
            ns('itemSet'),
            ns('newsItem'),
            ns('itemMeta'),
            ns('link'),
        ]))
        self.assertIsNotNone(link)
        self.assertEqual('image/jpeg', link.attrib['mimetype'])
        self.assertEqual('irel:seeAlso', link.attrib['rel'])
        self.assertIn('href', link.attrib)

        client = self.app.test_client()
        response = client.get(urlparse(link.attrib['href']).path)
        self.assertEqual(200, response.status_code, urlparse(link.attrib['href']).path)
        self.assertEqual(b'test', response.get_data())

    def test_html_void(self):
        """Check that HTML void element use self closing tags, but other elements with no content use start/end pairs

        SDESK-947 regression test
        """
        article = self.get_article()
        article['body_html'] = ('<p><h1>The story body</h1><h3/>empty element on purpose<br/><strong>test</strong>'
                                '<em/><br/>other test</p>')
        formatter = ANSANewsMLG2Formatter()
        _, doc = formatter.format(article, self.subscriber)[0]
        html_start = '<inlineXML contenttype="application/xhtml+xml">'
        html = doc[doc.find(html_start) + len(html_start):doc.find('</inlineXML>')]
        self.assertIn('<html>', html)
        self.assertIn('<body>', html)
        self.assertIn('<h1>The story body</h1>', html)

    def test_highlights(self):

        ids = self.app.data.insert('highlights', [
            {'name': 'Sports highlights'},
            {'name': 'Finance highlights'},
        ])

        article = self.get_article()
        article['highlights'] = ids
        seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(doc.encode('utf-8'))
        content_meta = get_content_meta(xml)
        subjects = content_meta.findall('{http://iptc.org/std/nar/2006-10-01/}subject[@type="highlight"]')
        self.assertEqual(2, len(subjects))
        self.assertEqual(subjects[0].attrib.get('id'), str(ids[0]))
        name = subjects[0].find(ns('name'))
        self.assertEqual('Sports highlights', name.text)

    def test_gallery(self):
        article = self.get_article()
        article['body_html'] = '<p>body</p>'
        article['associations'] = {
            'gallery--1': {
                'type': 'picture',
                'headline': 'foo',
                'renditions': {
                    'original': {
                        'media': 'picture1',
                        'width': 300,
                        'height': 200,
                    }
                }
            },
            'gallery--2': {
                'type': 'picture',
                'headline': 'bar',
                'renditions': {
                    'original': {
                        'media': 'picture2',
                    }
                }
            },
            'canceled': None,
        }

        xml = self.format(article)
        inline_xmls = xml.findall('.//%s' % ns('inlineXML'))
        self.assertEqual(2, len(inline_xmls))
        gallery = inline_xmls[1]
        self.assertEqual('gallery', gallery.get('rendition'))
        figures = gallery.findall('.//%s' % ns('figure'))
        self.assertEqual(2, len(figures))
        figure = figures[0]
        self.assertEqual(2, len(figure))
        img = figure[0]
        figcaption = figure[1]
        self.assertIn('src', img.attrib)
        self.assertTrue('foo', figcaption.text)

    def format(self, article):
        formatter = ANSANewsMLG2Formatter()
        _, doc = formatter.format(article, self.subscriber)[0]
        return etree.fromstring(doc.encode('utf-8'))

    def test_sign_off(self):
        content_meta = self.format_content_meta()
        creators = content_meta.findall(ns('creator'))
        self.assertEqual(1, len(creators))
        self.assertEqual('Foo', creators[0].get('literal'))

    def test_authors(self):
        self.app.data.insert('users', [
            {
                "_id": "test_id",
                "username": "author 1",
                "display_name": "John Doe",
                "is_author": True,
                'sign_off': 'JD',
            },
            {
                "_id": "test_id_2",
                "username": "author 2",
                "display_name": "Foo",
                "is_author": True,
                'sign_off': 'F',
            },
        ])

        updates = {'authors': [
            {
                'role': 'editor',
                'name': 'John Doe',
                'parent': 'test_id',
            },
            {
                'role': 'photographer',
                'name': 'photographer',
                'parent': 'test_id_2',
            },
        ]}

        content_meta = self.format_content_meta(updates)
        contributors = content_meta.findall(ns('contributor'))
        self.assertEqual(2, len(contributors))
        self.assertEqual('John Doe', contributors[0].find(ns('name')).text)
        self.assertEqual(contributors[0].get('literal'), 'JD')
        self.assertEqual('Foo', contributors[1].find(ns('name')).text)

    def test_headlines(self):
        content_meta = self.format_content_meta()
        headlines = content_meta.findall(ns('headline'))
        self.assertEqual(4, len(headlines))
        self.assertEqual('hld:subHeadline', headlines[1].get('role'))
        self.assertEqual('Subtitle text', headlines[1].text)
        self.assertEqual('hld:shortHeadline', headlines[2].get('role'))
        self.assertEqual('Short headline', headlines[2].text)
        self.assertEqual('hld:sms', headlines[3].get('role'))
        self.assertEqual('SMS message', headlines[3].text)

    def format_content_meta(self, updates=None):
        article = self.get_article(updates)
        xml = self.format(article)
        return get_content_meta(xml)

    def test_product_output_codes(self):
        content_meta = self.format_content_meta()
        subject = content_meta.find(ns('subject[@qcode="products:020002007289230000"]'))
        self.assertIsNotNone(subject)
        self.assertEqual('PHOTOMED', subject.find(ns('name')).text)

    def test_located(self):
        content_meta = self.format_content_meta()
        located = content_meta.find(ns('located'))
        self.assertIsNotNone(located)
        self.assertEqual('city:ROME', located.get('qcode'))
        broader = located.findall(ns('broader'))
        self.assertEqual(2, len(broader))
        self.assertEqual('reg:Latium', broader[0].get('qcode'))
        self.assertEqual('cntry:ITALY', broader[1].get('qcode'))

    def test_byline(self):
        content_meta = self.format_content_meta()
        byline = content_meta.find(ns('by'))
        self.assertEqual('joe', byline.text)

    def test_places(self):
        content_meta = self.format_content_meta()
        places = content_meta.findall(ns('subject[@type="cpnat:geoArea"]'))
        self.assertEqual(1, len(places))
        self.assertEqual('n:Roma', places[0].get('qcode'))
        self.assertEqual('Roma', places[0].find(ns('name')).text)

    def get_item(self, article_updates):
        article = self.get_article(article_updates)
        xml = self.format(article)
        return xml.find(ns('itemSet/') + ns('newsItem'))

    def test_use_original_ansa_id(self):
        updates = {'extra': {'ansaid': 'tag:ansa:foo'}}
        item = self.get_item(updates)
        self.assertEqual(updates['extra']['ansaid'], item.get('guid'))

        updates['original_id'] = 'some:other:id'
        item = self.get_item(updates)
        self.assertNotEqual(updates['extra']['ansaid'], item.get('guid'))

    def test_semantics(self):
        updates = {
            'semantics': {
                'persons': ['Giorgio Ferrero', 'Flavio'],
                'organizations': ['Biennale College', 'College Cinema'],
            },
            'company_codes': [],
        }

        meta = self.format_content_meta(updates)

        persons = meta.findall(ns('subject[@type="cpnat:person"]'))
        self.assertEqual(2, len(persons))
        self.assertEqual(updates['semantics']['persons'][0], persons[0].find(ns('name')).text)
        self.assertEqual(updates['semantics']['persons'][1], persons[1].find(ns('name')).text)

        orgs = meta.findall(ns('subject[@type="cpnat:organisation"]'))
        self.assertEqual(2, len(orgs))
        self.assertEqual(updates['semantics']['organizations'][0], orgs[0].find(ns('name')).text)
        self.assertEqual(updates['semantics']['organizations'][1], orgs[1].find(ns('name')).text)

    def test_format_geonames_city(self):
        updates = {'place': [geoname]}
        meta = self.format_content_meta(updates)

        places = meta.findall(ns('subject[@type="cptype:city"]'))
        self.assertEqual(1, len(places))

        place = places[0]
        self.assertEqual('geo:%s' % geoname['code'], place.get('qcode'))
        self.assertEqual(geoname['name'], place.find(ns('name')).text)

        continent = place.find(ns('broader[@type="cptype:continentalcode"]'))
        self.assertIsNotNone(continent)
        self.assertEqual('geo:EU', continent.get('qcode'))

        country = place.find(ns('broader[@type="cptype:country"]'))
        self.assertIsNotNone(country)
        self.assertEqual('geo:IT', country.get('qcode'))
        self.assertEqual(geoname['country'], country.find(ns('name')).text)

        region = place.find(ns('broader[@type="cptype:region"]'))
        self.assertIsNotNone(region)
        self.assertEqual('geo:%s' % geoname['state_code'], region.get('qcode'))
        self.assertEqual(geoname['state'], region.find(ns('name')).text)

        state = place.find(ns('broader[@type="cptype:statprov"]'))
        self.assertIsNotNone(state)
        self.assertEqual('geo:%s' % geoname['region_code'], state.get('qcode'))
        self.assertEqual(geoname['region'], state.find(ns('name')).text)

        geo = place.find(ns('geoAreaDetails'))
        self.assertIsNone(geo)

    def test_genre(self):
        meta = self.format_content_meta({})
        genre = meta.find(ns('genre'))
        self.assertIsNotNone(genre)
        self.assertEqual('genre:Article', genre.get('qcode'))
        self.assertEqual('Article (news)', genre.find(ns('name')).text)

    def test_located_semantics(self):
        updates = {'dateline': {'located': {'place': geoname}}}
        meta = self.format_content_meta(updates)
        located = meta.find(ns('located'))
        self.assertIsNotNone(located)
        self.assertEqual('geo:%s' % geoname['code'], located.get('qcode'))
        geo = located.find(ns('geoAreaDetails'))
        self.assertIsNotNone(geo)
        position = geo.find(ns('position'))
        self.assertIsNotNone(position)
        self.assertEqual(str(geoname['location']['lat']), position.get('latitude'))
        self.assertEqual(str(geoname['location']['lon']), position.get('longitude'))

    def test_desk_in_output(self):
        desks = [{'name': 'SPO - Sports'}]
        self.app.data.insert('desks', desks)
        article = self.article.copy()
        article['_id'] = article['guid']
        article['task'] = {'desk': desks[0]['_id']}
        self.app.data.insert('archive', [article])

        item = self.get_item({})
        service = item.find(ns('itemMeta')).find(ns('service'))
        self.assertIsNotNone(service)
        self.assertEqual(desks[0]['name'], service.find(ns('name')).text)

        signal = item.find(ns('itemMeta')).find(ns('signal[@qcode="red-address:SPO"]'))
        self.assertIsNotNone(signal)

    def test_dateline(self):
        datelines = {
            'it': '(ANSA) - Roma (foo), 01 AGO -',
            'en': '(ANSA) - Roma (foo), AUG 1 -',
            'de': '(ANSA) - Roma (foo), 1 AUG -',
            'es': '(ANSA) - Roma (foo) 1 AGO -',
            'pt': 'Roma (foo), 1 AGO (ANSA) -',
            'ar': '(ANSA) - ' + 'أغسطس' + ' 1 - Roma (foo) -',
        }

        for lang, expected in datelines.items():
            content_meta = self.format_content_meta({'language': lang})
            dateline = content_meta.find(ns('dateline'))
            self.assertEqual(expected, dateline.text, lang)

    def test_rewrite_guid_version(self):

        article1 = self.article.copy()
        article2 = self.article.copy()
        article3 = self.article.copy()

        article2['rewrite_of'] = article1['_id']
        article2['rewrite_sequence'] = 1
        article2['_id'] = article2['guid'] = 'bar'

        article3['rewrite_of'] = article2['_id']
        article3['rewrite_sequence'] = 2
        article3['_id'] = article3['guid'] = 'baz'

        self.app.data.insert('archive', [article1, article2, article3])

        item1 = self.get_item(article1)
        self.assertEqual(article1['guid'], item1.get('guid'))
        self.assertEqual('1', item1.get('version'))

        item2 = self.get_item(article2)
        self.assertEqual(article1['guid'], item2.get('guid'))
        self.assertEqual('2', item2.get('version'))

        item3 = self.get_item(article3)
        self.assertEqual(article1['guid'], item3.get('guid'))
        self.assertEqual('3', item3.get('version'))

    def test_empty_content(self):
        article = self.get_article()
        article.pop('body_html')
        formatter = ANSANewsMLG2Formatter()
        _, doc = formatter.format(article, self.subscriber)[0]
        xml = etree.fromstring(doc.encode('utf-8'))
        html = xml.find('/'.join([
            ns('itemSet'),
            ns('newsItem'),
            ns('contentSet'),
            ns('inlineXML'),
        ]))
        self.assertIsNotNone(html)
        self.assertIn(article['headline'], etree.tostring(html, method='text').decode('utf-8'))

    def test_picture_content_meta(self):
        updates = {'type': 'picture', 'copyrightholder': 'Foo'}
        content_meta = self.format_content_meta(updates)

        creditline = content_meta.find(ns('creditline'))
        self.assertEqual('Foo', creditline.text)

        genre = content_meta.find(ns('genre'))
        self.assertIsNone(genre)

        located = content_meta.find(ns('located'))
        self.assertIsNone(located)

    def test_right_info(self):
        item = self.get_item({'type': 'picture'})
        rights_info = item.find(ns('rightsInfo'))
        self.assertIsNotNone(rights_info)
        copyrightholder = rights_info.find(ns('copyrightHolder'))
        self.assertEqual('FOO', copyrightholder.get('literal'))
        copyrightnotice = rights_info.find(ns('copyrightNotice'))
        self.assertEqual('FOO 2018', copyrightnotice.text)
