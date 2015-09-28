# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from test_factory import SuperdeskTestCase
from eve.utils import date_to_str
from superdesk.utc import get_expiry_date, utcnow
from apps.archive.commands import RemoveExpiredSpikeContent, get_overdue_scheduled_items
from apps.archive.archive import SOURCE as ARCHIVE
from superdesk.errors import SuperdeskApiError
from datetime import timedelta
from apps.archive.common import validate_schedule, remove_media_files


class RemoveSpikedContentTestCase(SuperdeskTestCase):

    articles = [{'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4f9',
                 '_id': '1',
                 'type': 'text',
                 'last_version': 3,
                 '_current_version': 4,
                 'body_html': 'Test body',
                 'urgency': 4,
                 'headline': 'Two students missing',
                 'pubstatus': 'usable',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'ednote': 'Andrew Marwood contributed to this article',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject':[{'qcode': '17004000', 'name': 'Statistics'},
                            {'qcode': '04001002', 'name': 'Weather'}],
                 'state': 'draft',
                 'expiry': utcnow() + timedelta(minutes=20),
                 'unique_name': '#1'},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a974-xy4532fe33f9',
                 '_id': '2',
                 'last_version': 3,
                 '_current_version': 4,
                 'body_html': 'Test body of the second article',
                 'urgency': 4,
                 'headline': 'Another two students missing',
                 'pubstatus': 'usable',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'ednote': 'Andrew Marwood contributed to this article',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject':[{'qcode': '17004000', 'name': 'Statistics'},
                            {'qcode': '04001002', 'name': 'Weather'}],
                 'expiry': utcnow() + timedelta(minutes=20),
                 'state': 'draft',
                 'type': 'text',
                 'unique_name': '#2'},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4fa',
                 '_id': '3',
                 '_current_version': 4,
                 'body_html': 'Test body',
                 'urgency': 4,
                 'headline': 'Two students missing killed',
                 'pubstatus': 'usable',
                 'firstcreated': utcnow(),
                 'byline': 'By Alan Karben',
                 'ednote': 'Andrew Marwood contributed to this article killed',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                 'subject':[{'qcode': '17004000', 'name': 'Statistics'},
                            {'qcode': '04001002', 'name': 'Weather'}],
                 'state': 'draft',
                 'expiry': utcnow() + timedelta(minutes=20),
                 'type': 'text',
                 'unique_name': '#3'},
                {'guid': 'tag:localhost:2015:69b961ab-2816-4b8a-a584-a7b402fed4fc',
                 '_id': '4',
                 '_current_version': 3,
                 'state': 'draft',
                 'type': 'composite',
                 'groups': [{'id': 'root', 'refs': [{'idRef': 'main'}], 'role': 'grpRole:NEP'},
                            {
                                'id': 'main',
                                'refs': [
                                    {
                                        'location': 'archive',
                                        'guid': '1',
                                        'residRef': '1',
                                        'type': 'text'
                                    },
                                    {
                                        'location': 'archive',
                                        'residRef': '2',
                                        'guid': '2',
                                        'type': 'text'
                                    }
                                ],
                                'role': 'grpRole:main'}],
                 'firstcreated': utcnow(),
                 'expiry': utcnow() + timedelta(minutes=20),
                 'unique_name': '#4'},
                {'guid': 'tag:localhost:2015:69b961ab-4b8a-a584-2816-a7b402fed4fc',
                 '_id': '5',
                 '_current_version': 3,
                 'state': 'draft',
                 'type': 'composite',
                 'groups': [{'id': 'root', 'refs': [{'idRef': 'main'}, {'idRef': 'story'}], 'role': 'grpRole:NEP'},
                            {
                                'id': 'main',
                                'refs': [
                                    {
                                        'location': 'archive',
                                        'guid': '1',
                                        'residRef': '1',
                                        'type': 'text'
                                    }
                                ],
                                'role': 'grpRole:main'},
                            {
                                'id': 'story',
                                'refs': [
                                    {
                                        'location': 'archive',
                                        'guid': '4',
                                        'residRef': '4',
                                        'type': 'composite'
                                    }
                                ],
                                'role': 'grpRole:story'}],
                 'firstcreated': utcnow(),
                 'expiry': utcnow() + timedelta(minutes=20),
                 'unique_name': '#5'}]

    media = {
        'viewImage': {
            'media': '1592730d582080f4e9fcc2fcf43aa357bda0ed19ffe314ee3248624cd4d4bc54',
            'mimetype': 'image/jpeg',
            'href': 'http://192.168.220.209/api/upload/abc/raw?_schema=http',
            'height': 452,
            'width': 640
        },
        'thumbnail': {
            'media': '52250b4f37da50ee663fdbff057a5f064479f8a8bbd24fb8fdc06135d3f807bb',
            'mimetype': 'image/jpeg',
            'href': 'http://192.168.220.209/api/upload/abc/raw?_schema=http',
            'height': 120,
            'width': 169
        },
        'baseImage': {
            'media': '7a608aa8f51432483918027dd06d0ef385b90702bfeba84ac4aec38ed1660b18',
            'mimetype': 'image/jpeg',
            'href': 'http://192.168.220.209/api/upload/abc/raw?_schema=http',
            'height': 990,
            'width': 1400
        },
        'original': {
            'media': 'stub.jpeg',
            'mimetype': 'image/jpeg',
            'href': 'http://192.168.220.209/api/upload/stub.jpeg/raw?_schema=http',
            'height': 2475,
            'width': 3500
        }
    }

    def setUp(self):
        super().setUp()

    def test_query_getting_expired_content(self):
        with self.app.app_context():
            self.app.data.insert(ARCHIVE, [{'expiry': get_expiry_date(-10), 'state': 'spiked'}])
            self.app.data.insert(ARCHIVE, [{'expiry': get_expiry_date(0), 'state': 'spiked'}])
            self.app.data.insert(ARCHIVE, [{'expiry': get_expiry_date(10), 'state': 'spiked'}])
            self.app.data.insert(ARCHIVE, [{'expiry': get_expiry_date(20), 'state': 'spiked'}])
            self.app.data.insert(ARCHIVE, [{'expiry': get_expiry_date(30), 'state': 'spiked'}])
            self.app.data.insert(ARCHIVE, [{'expiry': None, 'state': 'spiked'}])
            self.app.data.insert(ARCHIVE, [{'unique_id': 97, 'state': 'spiked'}])

            now = date_to_str(utcnow())
            expired_items = RemoveExpiredSpikeContent().get_expired_items(now)
            self.assertEquals(2, expired_items.count())

    def test_query_removing_media_files_keeps(self):
        with self.app.app_context():
            self.app.data.insert(ARCHIVE, [{'state': 'spiked',
                                            'expiry': get_expiry_date(-10),
                                            'type': 'picture',
                                            'renditions': self.media}])

            self.app.data.insert('ingest', [{'type': 'picture', 'renditions': self.media}])
            self.app.data.insert('archive_versions', [{'type': 'picture', 'renditions': self.media}])
            self.app.data.insert('legal_archive', [{'_id': 1, 'type': 'picture', 'renditions': self.media}])
            self.app.data.insert('legal_archive_versions', [{'_id': 1, 'type': 'picture', 'renditions': self.media}])

            archive_items = self.app.data.find_all('archive', None)
            self.assertEqual(archive_items.count(), 1)
            deleted = remove_media_files(archive_items[0])
            self.assertFalse(deleted)

    def test_query_getting_overdue_scheduled_content(self):
        with self.app.app_context():
            self.app.data.insert(ARCHIVE, [{'publish_schedule': get_expiry_date(-10), 'state': 'published'}])
            self.app.data.insert(ARCHIVE, [{'publish_schedule': get_expiry_date(-10), 'state': 'scheduled'}])
            self.app.data.insert(ARCHIVE, [{'publish_schedule': get_expiry_date(0), 'state': 'spiked'}])
            self.app.data.insert(ARCHIVE, [{'publish_schedule': get_expiry_date(10), 'state': 'scheduled'}])
            self.app.data.insert(ARCHIVE, [{'unique_id': 97, 'state': 'spiked'}])

            now = date_to_str(utcnow())
            overdueItems = get_overdue_scheduled_items(now, 'archive')
            self.assertEquals(1, overdueItems.count())


class ArchiveTestCase(SuperdeskTestCase):
    def setUp(self):
        super().setUp()

    def test_validate_schedule(self):
        validate_schedule(utcnow() + timedelta(hours=2))

    def test_validate_schedule_date_with_datetime_as_string_raises_superdeskApiError(self):
        self.assertRaises(SuperdeskApiError, validate_schedule, "2015-04-27T10:53:48+00:00")

    def test_validate_schedule_date_with_datetime_in_past_raises_superdeskApiError(self):
        self.assertRaises(SuperdeskApiError, validate_schedule, utcnow() + timedelta(hours=-2))
