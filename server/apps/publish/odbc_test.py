# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.publish import SUBSCRIBER_TYPES

from test_factory import SuperdeskTestCase
import superdesk
from superdesk.publish import init_app
from superdesk.publish.transmitters.odbc import ODBCPublishService


class ODBCTests(SuperdeskTestCase):
    subscribers = [{"_id": "1", "name": "Test", "subscriber_type": SUBSCRIBER_TYPES.WIRE, "media_type": "media",
                    "is_active": True, "sequence_num_settings": {"max": 10, "min": 1},
                    "critical_errors": {"9004": True},
                    "destinations": [{"name": "AAP IPNEWS", "delivery_type": "odbc", "format": "AAP IPNEWS",
                                      "config": {"stored_procedure": "InsertNews"}
                                      }]
                    }]

    queue_items = [{"_id": "1", "state": "pending", "content_type": "text", "headline": "test", "unique_name": "#2034",
                    "publishing_action": "published", "published_seq_num": 4,
                    "destination": {"name": "AAP IPNEWS", "delivery_type": "odbc", "format": "AAP IPNEWS",
                                    "config": {"stored_procedure": "InsertNews"}
                                    },
                    "formatted_item": {
                        "ident": "0",
                        "selector_codes": '3**',
                        "wordcount": 313,
                        "texttab": "x",
                        "originator": "AAP",
                        "service_level": "a",
                        "keyword": "ROSS",
                        "subject": "crime, law and justice",
                        "category": "a",
                        "take_key": "Take-that",
                        "subject_detail": "international court or tribunal",
                        "subject_reference": "02011001",
                        "article_text": "THIS IS A TEST PLEASE IGNORE",
                        "priority": "u",
                        "headline": "TEST HEADLINE",
                        "usn": 68147,
                        "subject_matter": "international law",
                        "sequence": 117,
                        "news_item_type": "News",
                        "author": "",
                        "genre": "Current",
                        "fullStory": 1
                    },
                    "subscriber_id": "1", "item_id": "1", "item_version": 6
                    }]

    def setUp(self):
        super().setUp()

        self.subscribers[0]['destinations'][0]['config']['connection_string'] = \
            superdesk.app.config["ODBC_TEST_CONNECTION_STRING"]
        self.app.data.insert('subscribers', self.subscribers)

        self.queue_items[0]['destination']['config']['connection_string'] = \
            superdesk.app.config["ODBC_TEST_CONNECTION_STRING"]
        self.app.data.insert('publish_queue', self.queue_items)
        init_app(self.app)

    def test_transmit(self):
        if superdesk.app.config['ODBC_PUBLISH']:
            subscriber = self.app.data.find('subscribers', None, None)[0]

            publish_service = ODBCPublishService()
            ret = publish_service._transmit(self.queue_items[0], subscriber)
            self.assertGreater(ret, 0)
