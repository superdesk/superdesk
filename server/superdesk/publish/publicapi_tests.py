# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import json

from apps.archive import init_app
from superdesk import get_resource_service
from superdesk.publish.publicapi import PublicAPIPublishService
from superdesk.tests import TestCase
from datetime import datetime


class PublicAPITest(TestCase):
    def setUp(self):
        super().setUp()
        with self.app.app_context():
            init_app(self.app)

    def test_publicapi(self):
        archive_item = {
            "_id": "item1",
            "guid": "item1",
            "unique_name": "#9028",
            "version": "1",
            "type": "text",
            "original_creator": "user_id",
            "versioncreated": "2015-06-01T22:19:08+0000",
            "subject": [{"name": "medical research", "parent": "07000000", "qcode": "07005000"}],
            "anpa_category": [{"qcode": "a"}],
            "task": {
                "desk": "desk_id",
                "stage": "stage_id",
                "status": "todo",
                "user": "user_id"
            },
            "state": "submitted",
            "pubstatus": "usable",
            "urgency": 1,
            "byline": "John Doe",
            "language": "en",
            "headline": "some headline",
            "slugline": "some slugline",
            "body_html": "item content"
        }
        published_item = {
            "_id": "item1",
            "version": "1",
            "type": "text",
            "versioncreated": "2015-06-01T22:19:08+0000",
            "subject": [{"name": "medical research", "parent": "07000000", "qcode": "07005000"}],
            "pubstatus": "usable",
            "urgency": 1,
            "byline": "John Doe",
            "language": "en",
            "headline": "some headline",
            "body_html": "item content"
        }
        formatted_item = dict([('formatted_item', json.dumps(archive_item))])
        with self.app.app_context():
            publicapiService = get_resource_service('publish_items')
            try:
                service = PublicAPIPublishService()
                service._transmit(formatted_item, {})
                item = publicapiService.find_one(req=None, _id='item1')
                del item['_etag']
                del item['_created']
                del item['_updated']
                item['versioncreated'] = datetime.strftime(item['versioncreated'], self.app.config['DATE_FORMAT'])
                self.assertDictEqual(item, published_item, 'Invalid published item')
            finally:
                publicapiService.delete({'_id': 'item1'})
