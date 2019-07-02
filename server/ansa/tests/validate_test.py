
from superdesk.tests import TestCase
from ansa.validate import validate, MASK_FIELD


class ValidateTestCase(TestCase):

    def test_product_based_validation(self):
        self.app.data.insert('vocabularies', [{
            '_id': 'products',
            'items': [
                {'qcode': 'foo', 'name': 'Foo', MASK_FIELD: '000011111'},
                {'qcode': 'bar', 'name': 'Bar', MASK_FIELD: '111110000'},
                {'qcode': 'baz', 'name': 'Baz', MASK_FIELD: 'baz'},
            ],
        }])
        item = {
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
        fields = {}
        response = []
        validate(self, item, response, fields)
        self.assertIn('Headline is required', response)
        self.assertIn('Subtitle is required', response)
        self.assertIn('Short Title is required', response)
        self.assertIn('Subject is required', response)
        self.assertIn('Featured photo is required', response)
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
        item['associations'] = {'featuremedia': {'type': 'picture'}}
        item['photoGallery'] = {'type': 'picture'}
        item['subject'].append({'name': 'Test', 'qcode': '12345678'})
        item['body_html'] = 'short'
        validate(self, item, response, fields)
        self.assertEqual([], response)
