
import eve
import pytz
import unittest
import superdesk

from datetime import datetime
from unittest.mock import patch, ANY
from ansa.vfs import VFSMediaStorage
from ansa.save_iptc import init_app
from ansa.constants import PHOTO_CATEGORIES_ID


class UpdateIPTCMetadataTestCase(unittest.TestCase):

    def setUp(self):
        self.app = eve.Eve(media=VFSMediaStorage, settings={'DOMAIN': {}})
        init_app(self.app)

    def test_update_iptc_metadata_on_publish(self):
        item = {
            'type': 'picture',
            'pubstatus': 'usable',
            'language': 'cs',
            'headline': 'head',
            'slugline': 'slug',
            'description_text': 'desc',
            'sign_off': 'JD',
            'byline': 'John Doe',
            'copyrightholder': 'copy holder',
            'copyrightnotice': 'copy notice',
            'usageterms': 'usage',
            'firstpublished': datetime(2019, 9, 20, 12, 0, 0, tzinfo=pytz.utc),
            'firstcreated': datetime(2019, 9, 20, 10, 0, 0, tzinfo=pytz.utc),
            'extra': {
                'city': 'Prague',
                'nation': 'Czechia',
                'signature': 'sign',
                'DateRelease': 'DateRelease',
                'DateCreated': 'DateCreated',
                'digitator': 'digi',
            },
            'renditions': {
                'original': {
                    'href': 'foo',
                    'media': 'orig',
                },
            },
            'subject': [
                {'name': 'Foo', 'qcode': '01000000'},
                {'name': 'Bar', 'qcode': '02000000', 'scheme': PHOTO_CATEGORIES_ID},
                {'name': 'Prod A', 'qcode': '001', 'scheme': 'products'},
                {'name': 'Prod B', 'qcode': '002', 'scheme': 'products'},
            ],
        }

        with self.app.app_context():
            with patch.object(self.app.media, 'put_metadata', return_value='bar') as put_mock:
                superdesk.item_publish.send(self, item=item)
                put_mock.assert_called_once_with('orig', ANY)
                meta = put_mock.call_args[0][1]
                self.maxDiff = None
                self.assertDictEqual(meta, {
                    'language': item['language'],
                    'categoryAnsa': item['subject'][1]['name'],
                    'categorySupAnsa': item['slugline'],
                    'city': item['extra']['city'],
                    'ctrName': item['extra']['nation'],
                    'title_B': item['headline'],
                    'description_B': item['description_text'],
                    'signoff': item['sign_off'],
                    'contentBy': item['byline'],
                    'signature': item['extra']['signature'],
                    'supplier': 'ANSA',
                    'copyrightHolder': item['copyrightholder'],
                    'copyrightNotice': item['copyrightnotice'],
                    'usageTerms': item['usageterms'],
                    'pubDate_N': '2019-09-20T12:00:00+00:00',
                    'releaseDate': item['extra']['DateRelease'],
                    'dateCreated': item['extra']['DateCreated'],
                    'digitator': item['extra']['digitator'],
                    'status': 'stat:usable',
                    'product': [
                        item['subject'][2]['qcode'],
                        item['subject'][3]['qcode'],
                    ],
                })

        self.assertEqual('bar', item['renditions']['original']['media'])
        self.assertIn('bar', item['renditions']['original']['href'])

    def test_ignore_non_picture_items(self):
        item = {'type': 'video'}
        superdesk.item_publish.send(self, item=item)
