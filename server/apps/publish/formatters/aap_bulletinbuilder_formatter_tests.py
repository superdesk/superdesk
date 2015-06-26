# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.tests import TestCase
from apps.publish import init_app
from apps.publish.formatters.aap_bulletinbuilder_formatter import AAPBulletinBuilderFormatter
from superdesk.utils import json_serialize_datetime_objectId
from superdesk import json
from superdesk.utc import utcnow
from bson import ObjectId


class AapBulletinBuilderFormatterTest(TestCase):
    subscribers = [{"_id": "1", "name": "Test", "can_send_takes_packages": False, "media_type": "media",
                    "is_active": True, "sequence_num_settings": {"max": 10, "min": 1},
                    "destinations": [{"name": "AAP Bulletin Builder", "delivery_type": "pull",
                                      "format": "AAP BULLETIN BUILDER"
                                      }]
                    }]

    article = {
        'source': 'AAP',
        'anpa-category': {'qcode': 'a'},
        'headline': 'This is a test headline',
        'byline': 'joe',
        'slugline': 'slugline',
        'subject': [{'qcode': '02011001'}],
        'anpa_take_key': 'take_key',
        'unique_id': '1',
        'type': 'preformatted',
        'body_html': 'The story body',
        'word_count': '1',
        'priority': '1',
        'firstcreated': utcnow(),
        'versioncreated': utcnow(),
        'lock_user': ObjectId()
    }

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.app.data.insert('subscribers', self.subscribers)
            init_app(self.app)

    def TestBulletinBuilderFormatter(self):
        with self.app.app_context():
            subscriber = self.app.data.find('subscribers', None, None)[0]
            f = AAPBulletinBuilderFormatter()
            seq, item = f.format(self.article, subscriber)
            self.assertGreater(int(seq), 0)
            self.assertEquals(json.dumps(self.article, default=json_serialize_datetime_objectId), item)
