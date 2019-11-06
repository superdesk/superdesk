
from superdesk.tests import TestCase
from ansa.validate import validate, MASK_FIELD


class ValidateTestCase(TestCase):

    def setUp(self):
        self.app.data.insert('vocabularies', [{
            '_id': 'products',
            'items': [
                {'qcode': 'foo', 'name': 'Foo', MASK_FIELD: '000011111'},
                {'qcode': 'bar', 'name': 'Bar', MASK_FIELD: 111110000},
                {'qcode': 'baz', 'name': 'Baz', MASK_FIELD: 'baz'},
            ],
        }])
        self.item = {
            'subject': [
                {
                    'qcode': 'foo',
                    'scheme': 'products',
                },
                {
                    'qcode': 'bar',
                    'scheme': 'products',
                },
                {
                    'qcode': 'baz',
                    'scheme': 'products',
                },
            ],
        }

    def test_product_based_validation(self):
        item = self.item.copy()
        fields = {}
        response = []
        validate(self, item, response, fields)
        self.assertIn('Headline is required', response)
        self.assertIn('Subtitle is required', response)
        self.assertIn('Short Title is required', response)
        self.assertIn('Subject is required', response)
        self.assertIn('Photo is required', response)
        self.assertIn('Photo gallery is required', response)
        self.assertEqual(6, len(response))

        response = []
        item['body_html'] = '<p>{}</p>'.format('x' * 1000)
        validate(self, item, response, fields)
        self.assertIn('Body is longer than 512 characters', response)
        self.assertEqual(7, len(response))

        response = []
        item['headline'] = 'foo'
        item['extra'] = {'subtitle': 'foo', 'shorttitle': 'bar'}
        item['associations'] = {
            'featuremedia': {'type': 'picture'},
            'photoGallery--1': {'type': 'picture'},
        }
        item['subject'].append({'name': 'Test', 'qcode': '12345678'})
        item['body_html'] = 'short'
        validate(self, item, response, fields)
        self.assertEqual([], response)

    def test_auto_publish_skip_validation(self):
        item = self.item.copy()
        item['auto_publish'] = True
        fields = {}
        response = []
        validate(self, item, response, fields)
        self.assertEqual([], response)
