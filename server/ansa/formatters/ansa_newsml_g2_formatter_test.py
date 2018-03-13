
import io
import os
import tempfile
from lxml import etree
from unittest import mock

from superdesk.utc import utcnow
from superdesk.tests import TestCase
from .ansa_newsml_g2_formatter import ANSANewsMLG2Formatter


def ns(value):
    return '{http://iptc.org/std/nar/2006-10-01/}%s' % value


@mock.patch('superdesk.publish.subscribers.SubscribersService.generate_sequence_number', lambda self, subscriber: 1)
class ANSANewsmlG2FormatterTestCase(TestCase):
    formatter = ANSANewsMLG2Formatter()

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
        'body_html': '<p>The story body <b>HTML</b></p><p>another paragraph</p><style></style>',
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
        'company_codes': [{'name': 'YANCOAL AUSTRALIA LIMITED', 'qcode': 'YAL', 'security_exchange': 'ASX'}],
    }

    vocab = [{'_id': 'rightsinfo', 'items': [{'name': 'AAP',
                                              'copyrightHolder': 'copy right holder',
                                              'copyrightNotice': 'copy right notice',
                                              'usageTerms': 'terms'},
                                             {'name': 'default',
                                              'copyrightHolder': 'default copy right holder',
                                              'copyrightNotice': 'default copy right notice',
                                              'usageTerms': 'default terms'}]}]

    dest = {'config': {'file_path': tempfile.gettempdir()}}
    subscriber = {'_id': 'foo', 'name': 'Foo', 'config': {}, 'destinations': [dest]}

    def setUp(self):
        self.app.data.insert('vocabularies', self.vocab)

    def get_article(self):
        article = self.article.copy()
        article['firstcreated'] = article['versioncreated'] = utcnow()
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
        article = self.get_article()
        article['associations'] = {
            'featuremedia': {
                'type': 'picture',
                'renditions': {
                    'original': {
                        'mimetype': 'image/jpeg',
                        'media': 'featured'
                    }
                }
            }
        }

        formatter = ANSANewsMLG2Formatter()
        with mock.patch('superdesk.app.media.get', return_value=io.BytesIO(b'test')):
            _, doc = formatter.format(article, self.subscriber)[0]
        self.assertIn('<link', doc)
        xml = etree.fromstring(doc.encode('utf-8'))
        link = xml.find(
            '{http://iptc.org/std/nar/2006-10-01/}itemSet/{http://iptc.org/std/nar/2006-10-01/}newsItem/' +
            '{http://iptc.org/std/nar/2006-10-01/}itemMeta/{http://iptc.org/std/nar/2006-10-01/}link')
        self.assertIsNotNone(link)
        self.assertEqual('image/jpeg', link.attrib['mimetype'])
        self.assertEqual('irel:seeAlso', link.attrib['rel'])
        self.assertIn('href', link.attrib)
        filepath = os.path.join(self.dest['config']['file_path'], link.attrib['href'])
        self.assertTrue(os.path.exists(filepath))
        with open(filepath, 'rb') as related:
            self.assertEqual(b'test', related.read())

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
        expected = ('<html><body><p></p><h1>The story body</h1><h3></h3>empty element on purpose<br/>'
                    '<strong>test</strong><em></em><br/>other test</body></html>')
        self.assertEqual(html, expected)

    def test_highlights(self):

        ids = self.app.data.insert('highlights', [
            {'name': 'Sports highlights'},
            {'name': 'Finance highlights'},
        ])

        article = self.get_article()
        article['highlights'] = ids
        seq, doc = self.formatter.format(article, {'name': 'Test Subscriber'})[0]
        xml = etree.fromstring(doc.encode('utf-8'))
        content_meta = xml.find('{http://iptc.org/std/nar/2006-10-01/}itemSet'
                                '/{http://iptc.org/std/nar/2006-10-01/}newsItem/'
                                '{http://iptc.org/std/nar/2006-10-01/}contentMeta')
        subjects = content_meta.findall('{http://iptc.org/std/nar/2006-10-01/}subject[@type="highlight"]')
        self.assertEqual(2, len(subjects))
        self.assertEqual(subjects[0].attrib.get('id'), str(ids[0]))
        name = subjects[0].find('{http://iptc.org/std/nar/2006-10-01/}name')
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
        }

        with mock.patch('superdesk.app.media.get', return_value=io.BytesIO(b'test')):
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
        self.assertTrue(os.path.exists(os.path.join(self.dest['config']['file_path'], img.get('src'))))
        self.assertTrue('foo', figcaption.text)

    def format(self, article):
        formatter = ANSANewsMLG2Formatter()
        _, doc = formatter.format(article, self.subscriber)[0]
        return etree.fromstring(doc.encode('utf-8'))
