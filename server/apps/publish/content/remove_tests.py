# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from datetime import timedelta
import os
import json

from eve.utils import config
from eve.versioning import versioned_id_field

from apps.archive.common import insert_into_versions, is_takes_package, ITEM_OPERATION
from apps.packages.package_service import PackageService
from apps.packages.takes_package_service import TakesPackageService
from superdesk.publish.subscribers import SUBSCRIBER_TYPES
from apps.validators import ValidatorsPopulateCommand
from superdesk.metadata.packages import RESIDREF, GROUPS
from test_factory import SuperdeskTestCase
from apps.publish import init_app, RemoveExpiredPublishContent
from apps.legal_archive import LEGAL_ARCHIVE_NAME, LEGAL_ARCHIVE_VERSIONS_NAME, LEGAL_PUBLISH_QUEUE_NAME
from superdesk.utc import utcnow
from superdesk import get_resource_service
from apps.archive.archive import SOURCE as ARCHIVE
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE, ITEM_TYPE, CONTENT_TYPE

from .tests import ARCHIVE_PUBLISH, ARCHIVE_KILL, PUBLISHED


class RemoveExpiredFromPublishedCollection(SuperdeskTestCase):
    def setUp(self):
        super().setUp()
        self._init_data()

        self.app.data.insert('vocabularies', self.vocabularies)
        self.app.data.insert('subscribers', self.subscribers)
        self.app.data.insert(ARCHIVE, self.articles)

        self.filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), "validators.json")
        self.json_data = [
            {"_id": "kill_text", "act": "kill", "type": "text", "schema": {"headline": {"type": "string"}}},
            {"_id": "publish_text", "act": "publish", "type": "text", "schema": {}},
            {"_id": "correct_text", "act": "correct", "type": "text", "schema": {}},
            {"_id": "publish_composite", "act": "publish", "type": "composite", "schema": {}},
        ]

        with open(self.filename, "w+") as file:
            json.dump(self.json_data, file)
        init_app(self.app)
        ValidatorsPopulateCommand().run(self.filename)

        self.package_service = PackageService()

    def tearDown(self):
        super().tearDown()
        if self.filename and os.path.exists(self.filename):
            os.remove(self.filename)

    def test_can_remove_from_production_succeeds_when_published_once(self):
        """
        Tests if can_remove_production() returns true if the item is published only once.
        """

        doc = self.articles[0].copy()

        updates = {'targeted_for': [{'name': 'New South Wales', 'allow': True}]}
        get_resource_service(ARCHIVE).patch(id=doc[config.ID_FIELD], updates=updates)

        published_version_number = doc[config.VERSION] + 1
        get_resource_service(ARCHIVE_PUBLISH).patch(id=doc[config.ID_FIELD],
                                                    updates={ITEM_STATE: CONTENT_STATE.PUBLISHED,
                                                             config.VERSION: published_version_number})

        self._move_to_archived_and_assert_can_remove_from_production(doc[config.ID_FIELD], self.assertTrue)

    def test_can_remove_from_production_fails_when_published_and_then_killed(self):
        """
        Tests if can_remove_production() returns false if the item is published more than once.
        """

        doc = self.articles[0].copy()

        updates = {'targeted_for': [{'name': 'New South Wales', 'allow': True}]}
        get_resource_service(ARCHIVE).patch(id=doc[config.ID_FIELD], updates=updates)

        published_version_number = doc[config.VERSION] + 1
        get_resource_service(ARCHIVE_PUBLISH).patch(id=doc[config.ID_FIELD],
                                                    updates={ITEM_STATE: CONTENT_STATE.PUBLISHED,
                                                             config.VERSION: published_version_number})

        published_item = self._move_to_archived_and_assert_can_remove_from_production(doc[config.ID_FIELD],
                                                                                      self.assertTrue)

        published_version_number += 1
        get_resource_service(ARCHIVE_KILL).patch(id=doc['_id'],
                                                 updates={ITEM_STATE: CONTENT_STATE.KILLED,
                                                          config.VERSION: published_version_number})
        self.assertFalse(get_resource_service(PUBLISHED).can_remove_from_production(published_item))

    def test_can_remove_from_production_second_rule(self):
        """
        Test if can_remove_production() returns false when the expired published item is part of a package.
        """

        doc = self.articles[0].copy()

        get_resource_service(ARCHIVE_PUBLISH).patch(id=doc[config.ID_FIELD],
                                                    updates={ITEM_STATE: CONTENT_STATE.PUBLISHED,
                                                             config.VERSION: doc[config.VERSION] + 1})

        item_in_production = get_resource_service(ARCHIVE).find_one(req=None, _id=doc[config.ID_FIELD])
        self.assertIsNotNone(TakesPackageService().get_take_package_id(item_in_production))

        self._move_to_archived_and_assert_can_remove_from_production(doc[config.ID_FIELD], self.assertFalse)

    def test_can_remove_from_production_third_rule(self):
        """
        Test if can_remove_production() returns false when the expired published item is a package.
        """

        published_articles = [self.articles[1].copy(), self.articles[2].copy(), self.articles[3].copy(),
                              self.articles[4].copy()]

        for published_article in published_articles:
            published_article[ITEM_STATE] = CONTENT_STATE.PUBLISHED

        published_service = get_resource_service(PUBLISHED)
        published_service.post(published_articles)

        published_package = self._move_to_archived_and_assert_can_remove_from_production(
            self.articles[4][config.ID_FIELD], self.assertFalse)

        self._move_to_archived_and_assert_can_remove_from_production(self.articles[3][config.ID_FIELD],
                                                                     self.assertFalse, published_package)

        self._move_to_archived_and_assert_can_remove_from_production(self.articles[2][config.ID_FIELD],
                                                                     self.assertFalse, published_package)
        self._move_to_archived_and_assert_can_remove_from_production(self.articles[1][config.ID_FIELD],
                                                                     self.assertTrue, published_package)

    def test_cannot_remove_scheduled_content(self):
        published_service = get_resource_service(PUBLISHED)
        original = self.articles[0].copy()

        original[ITEM_STATE] = CONTENT_STATE.SCHEDULED
        original['publish_schedule'] = utcnow() + timedelta(days=2)

        published_service.post([original])
        published_items = published_service.get_other_published_items(original['item_id'])
        self.assertEqual(1, published_items.count())

        RemoveExpiredPublishContent().run()
        published_items = published_service.get_other_published_items(original['item_id'])
        self.assertEqual(1, published_items.count())

    def test_remove_published_expired_content(self):
        original = self.articles[0].copy()
        original[ITEM_STATE] = CONTENT_STATE.PUBLISHED
        self._create_and_insert_into_versions(original, True)

        published_service = get_resource_service(PUBLISHED)
        archive_publish = get_resource_service(ARCHIVE_PUBLISH)

        subscribers, subscribers_yet_to_receive = archive_publish.get_subscribers(original, SUBSCRIBER_TYPES.WIRE)
        archive_publish.queue_transmission(original, subscribers)
        published_service.post([original])

        published_items = published_service.get(req=None, lookup=None)
        self.assertEqual(1, published_items.count())

        published_service.update_published_items(original['item_id'], 'expiry', utcnow() + timedelta(minutes=-60))
        RemoveExpiredPublishContent().run()
        published_items = published_service.get_other_published_items(str(original['item_id']))
        self.assertEqual(0, published_items.count())

        archived_item = get_resource_service('archived').find_one(req=None, _id=str(original[config.ID_FIELD]))
        self.assertEqual(archived_item['item_id'], self.articles[0][config.ID_FIELD])
        self.assertFalse(archived_item['allow_post_publish_actions'])
        self.assertFalse(archived_item['can_be_removed'])

        article_in_legal_archive, article_versions_in_legal_archive, queue_items = \
            self._get_legal_archive_details(original['item_id'])

        self.assertIsNotNone(article_in_legal_archive, 'Article cannot be none in Legal Archive')

        self.assertIsNotNone(article_versions_in_legal_archive, 'Article Versions cannot be none in Legal Archive')
        self.assertEqual(article_versions_in_legal_archive.count(), 4)

        self.assertGreaterEqual(queue_items.count(), 1, 'Publish Queue Items must be greater than or equal to 1')
        for queue_item in queue_items:
            self.assertEqual(queue_item['item_id'], self.articles[0]['_id'])
            self.assertEqual(queue_item['item_version'], original[config.VERSION])

    def test_remove_published_and_killed_content_separately(self):
        doc = self.articles[0]
        original = doc.copy()

        updates = {'targeted_for': [{'name': 'New South Wales', 'allow': True}]}
        get_resource_service(ARCHIVE).patch(id=original[config.ID_FIELD], updates=updates)

        original.update(updates)
        self._create_and_insert_into_versions(original, False)

        published_version_number = original[config.VERSION] + 1
        get_resource_service(ARCHIVE_PUBLISH).patch(id=doc[config.ID_FIELD],
                                                    updates={ITEM_STATE: CONTENT_STATE.PUBLISHED,
                                                             config.VERSION: published_version_number})

        published_service = get_resource_service(PUBLISHED)
        published_items = published_service.get(req=None, lookup=None)
        self.assertEqual(1, published_items.count())

        article_in_production = get_resource_service(ARCHIVE).find_one(req=None, _id=original[config.ID_FIELD])
        self.assertIsNotNone(article_in_production)
        self.assertEqual(article_in_production[ITEM_STATE], CONTENT_STATE.PUBLISHED)
        self.assertEqual(article_in_production[config.VERSION], published_version_number)
        insert_into_versions(doc=article_in_production)

        # Setting the expiry date of the published article to 1 hr back from now
        published_service.update_published_items(
            original[config.ID_FIELD], 'expiry', utcnow() + timedelta(minutes=-60))

        # Killing the published article and inserting into archive_versions as unittests use service directly
        published_version_number += 1
        get_resource_service(ARCHIVE_KILL).patch(id=doc[config.ID_FIELD],
                                                 updates={ITEM_STATE: CONTENT_STATE.KILLED,
                                                          config.VERSION: published_version_number})

        # Executing the Expiry Job for the Published Article and asserting the collections
        RemoveExpiredPublishContent().run()

        published_items = published_service.get(req=None, lookup=None)
        self.assertEqual(1, published_items.count())

        article_in_production = get_resource_service(ARCHIVE).find_one(req=None, _id=original[config.ID_FIELD])
        self.assertIsNotNone(article_in_production)
        self.assertEqual(article_in_production[ITEM_STATE], CONTENT_STATE.KILLED)
        self.assertEqual(article_in_production[config.VERSION], published_version_number)
        insert_into_versions(doc=article_in_production)

        # Validate the collections in Legal Archive
        article_in_legal_archive, article_versions_in_legal_archive, queue_items = \
            self._get_legal_archive_details(original[config.ID_FIELD])

        self.assertIsNotNone(article_in_legal_archive, 'Article cannot be none in Legal Archive')
        self.assertEqual(article_in_legal_archive[ITEM_STATE], CONTENT_STATE.PUBLISHED)

        self.assertIsNotNone(article_versions_in_legal_archive, 'Article Versions cannot be none in Legal Archive')
        self.assertEqual(article_versions_in_legal_archive.count(), 5)

        self.assertEqual(queue_items.count(), 1)

        # Setting the expiry date of the killed article to 1 hr back from now and running the job again
        published_service.update_published_items(
            original[config.ID_FIELD], 'expiry', utcnow() + timedelta(minutes=-60))
        RemoveExpiredPublishContent().run()

        published_items = published_service.get_other_published_items(str(original[config.ID_FIELD]))
        self.assertEqual(0, published_items.count())

        article_in_production = get_resource_service(ARCHIVE).find_one(req=None, _id=original[config.ID_FIELD])
        self.assertIsNone(article_in_production)

        # Validate the collections in Legal Archive
        article_in_legal_archive, article_versions_in_legal_archive, queue_items = \
            self._get_legal_archive_details(original[config.ID_FIELD], publishing_action='killed')

        self.assertIsNotNone(article_in_legal_archive, 'Article cannot be none in Legal Archive')
        self.assertEqual(article_in_legal_archive[ITEM_STATE], CONTENT_STATE.KILLED)

        self.assertIsNotNone(article_versions_in_legal_archive, 'Article Versions cannot be none in Legal Archive')
        self.assertEqual(article_versions_in_legal_archive.count(), 6)

        for queue_item in queue_items:
            self.assertEqual(queue_item['item_id'], original[config.ID_FIELD])
            self.assertEqual(queue_item['item_version'], published_version_number)

        self.assertEqual(queue_items.count(), 1)

    def test_remove_takes_package(self):
        """
        Tests the behavior of remove_expired() when just takes package expires
        """

        def expire_and_assert_legal_archive(published_takes_pkg, version_count, item_count_in_pub_queue):
            published_service.update(published_takes_pkg[config.ID_FIELD],
                                     {'expiry': utcnow() + timedelta(minutes=-60)}, published_takes_pkg)

            RemoveExpiredPublishContent().run()
            article_in_legal_archive, article_versions_in_legal_archive, queue_items = \
                self._get_legal_archive_details(published_takes_pkg['item_id'])

            self.assertIsNotNone(article_in_legal_archive, 'Article cannot be none in Legal Archive')
            self.assertEqual(article_in_legal_archive[ITEM_STATE], published_takes_pkg[ITEM_STATE])

            self.assertIsNotNone(article_versions_in_legal_archive, 'Article Versions cannot be none in Legal Archive')
            self.assertEqual(article_versions_in_legal_archive.count(), version_count)

            self.assertEqual(queue_items.count(), item_count_in_pub_queue)

            legal_archive_service = get_resource_service(LEGAL_ARCHIVE_NAME)
            item_ref = self.package_service.get_item_refs(article_in_legal_archive)
            item_ref = item_ref[0]

            self.assertEqual(item_ref.get('location', ARCHIVE), LEGAL_ARCHIVE_NAME)

            query = {'$and': [{config.ID_FIELD: item_ref[RESIDREF]}, {config.VERSION: item_ref[config.VERSION]}]}
            package_item_in_legal_archive = legal_archive_service.get_from_mongo(req=None, lookup=query)

            self.assertEqual(package_item_in_legal_archive.count(), 1)
            for item in package_item_in_legal_archive:
                package_item_in_legal_archive = item

            if published_takes_pkg[ITEM_STATE] == CONTENT_STATE.PUBLISHED:
                self.assertEqual(published_takes_pkg[ITEM_OPERATION], 'publish')
                self.assertEqual(package_item_in_legal_archive[ITEM_OPERATION], 'publish')
            elif published_takes_pkg[ITEM_STATE] == CONTENT_STATE.KILLED:
                self.assertEqual(published_takes_pkg[ITEM_OPERATION], 'kill')
                self.assertEqual(package_item_in_legal_archive[ITEM_OPERATION], 'kill')

        doc = self.articles[0].copy()
        self._create_and_insert_into_versions(doc, False)

        published_version_number = doc[config.VERSION] + 1
        get_resource_service(ARCHIVE_PUBLISH).patch(id=doc[config.ID_FIELD],
                                                    updates={ITEM_STATE: CONTENT_STATE.PUBLISHED,
                                                             config.VERSION: published_version_number})
        insert_into_versions(id_=doc[config.ID_FIELD])

        published_version_number += 1
        get_resource_service(ARCHIVE_KILL).patch(id=doc[config.ID_FIELD],
                                                 updates={ITEM_STATE: CONTENT_STATE.KILLED,
                                                          config.VERSION: published_version_number})
        insert_into_versions(id_=doc[config.ID_FIELD])

        published_service = get_resource_service(PUBLISHED)
        items_in_published_repo = list(published_service.get_from_mongo(req=None, lookup=None))
        self.assertEqual(len(items_in_published_repo), 4)

        # Expiring the Takes Package whose state is Published
        published_takes_pkg = [g for g in items_in_published_repo if is_takes_package(g) and
                               g[ITEM_STATE] == CONTENT_STATE.PUBLISHED]
        expire_and_assert_legal_archive(published_takes_pkg[0], 2, 1)

        # Expiring the Takes Package whose state is Killed
        published_takes_pkg = [g for g in items_in_published_repo if is_takes_package(g) and
                               g[ITEM_STATE] == CONTENT_STATE.KILLED]
        expire_and_assert_legal_archive(published_takes_pkg[0], 3, 2)

    def test_remove_when_package_and_items_in_package_expire(self):
        """
        Tests if items in the package are copied to legal archive when the package in published collection expires.
        In this test both the items in the package and package expire. Since the job sorts the expired items in the
        order they are created, the creation order of items in this test is: items in the package and then the package.
        """

        package = self.articles[3].copy()

        items_in_published_repo = self._publish_package_and_assert_published_collection(package)
        published_service = get_resource_service(PUBLISHED)

        # Validate if version is available for each item in the package after publishing
        for item in items_in_published_repo:
            if item[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
                items_in_package = self.package_service.get_item_refs(package)
                for item_in_pkg in items_in_package:
                    if config.VERSION not in item_in_pkg:
                        self.fail('version is not found for item in the package. Item Id: %s' % item_in_pkg['guid'])

            # Expiring the published items
            published_service.update_published_items(item['item_id'], 'expiry', utcnow() + timedelta(minutes=-60))

        RemoveExpiredPublishContent().run()
        self.assertEqual(published_service.get(req=None, lookup=None).count(), 0)

        article_in_legal_archive, article_versions_in_legal_archive, queue_items = \
            self._get_legal_archive_details(package[config.ID_FIELD])
        self.assertIsNotNone(article_in_legal_archive)

        item_refs = self.package_service.get_item_refs(article_in_legal_archive)
        for ref in item_refs:
            self.assertEqual(ref.get('location', ARCHIVE), LEGAL_ARCHIVE_NAME)

    def test_remove_when_only_package_expires(self):
        """
        Tests if items in the package are copied to legal archive when only the package in published collection expires.
        In this test only the package expires. Since the job sorts the expired items in the order they are created,
        the creation order of items in this test is: items in the package and then the package.
        """

        package = self.articles[3].copy()

        self._publish_package_and_assert_published_collection(package)
        published_service = get_resource_service(PUBLISHED)

        # Expiring the package
        published_service.update_published_items(package[config.ID_FIELD], 'expiry',
                                                 utcnow() + timedelta(minutes=-60))

        RemoveExpiredPublishContent().run()
        items_in_published_repo = published_service.get(req=None, lookup=None)
        self.assertEqual(items_in_published_repo.count(), 2)

        for item in items_in_published_repo:
            self.assertTrue(item['allow_post_publish_actions'])

        article_in_legal_archive, article_versions_in_legal_archive, queue_items = \
            self._get_legal_archive_details(package[config.ID_FIELD])
        self.assertIsNotNone(article_in_legal_archive)

        item_refs = self.package_service.get_item_refs(article_in_legal_archive)
        for ref in item_refs:
            self.assertEqual(ref.get('location', ARCHIVE), LEGAL_ARCHIVE_NAME)

    def _publish_package_and_assert_published_collection(self, package):
        # Please make sure that groups has only text items
        item_refs = self.package_service.get_residrefs(package)

        # Inserting docs into archive_versions for all items in the package and for the package
        for item_ref in item_refs:
            item = None
            for article in self.articles:
                if article[config.ID_FIELD] == item_ref:
                    item = article
                    break

            item = item.copy()
            updates = {'targeted_for': [{'name': 'Wire', 'allow': True}]}
            get_resource_service(ARCHIVE).patch(id=item[config.ID_FIELD], updates=updates)

            self._create_and_insert_into_versions(item, False)

        self._create_and_insert_into_versions(package, False)

        updates = {ITEM_STATE: CONTENT_STATE.PUBLISHED, config.VERSION: package[config.VERSION] + 1,
                   GROUPS: package.get(GROUPS)}
        get_resource_service(ARCHIVE_PUBLISH).patch(id=package[config.ID_FIELD], updates=updates)

        items_in_published_repo = get_resource_service(PUBLISHED).get_from_mongo(req=None, lookup=None)
        self.assertEqual(items_in_published_repo.count(), 3)

        return items_in_published_repo

    def _init_data(self):
        self.vocabularies = [
            {"_id": "rightsinfo", "items": [
                {"is_active": True, "name": "AAP", "copyrightHolder": "Australian Associated Press",
                 "copyrightNotice": "AAP content is owned by or licensed to AAP",
                 "usageTerms": "The direct recipient must comply with the limitations specified in the AAP Information"
                 },
                {"is_active": True, "name": "default", "copyrightHolder": "Australian Associated Press",
                 "copyrightNotice": "AAP content is owned by or licensed to AAP.",
                 "usageTerms": "The direct recipient must comply with the limitations specified in the AAP Information."
                 }]
             }
        ]

        self.subscribers = [{"_id": "1", "name": "sub1", "is_active": True, "subscriber_type": SUBSCRIBER_TYPES.WIRE,
                             "media_type": "media", "sequence_num_settings": {"max": 10, "min": 1},
                             "email": "test@test.com",
                             "destinations": [{"name": "dest1", "format": "nitf", "delivery_type": "ftp",
                                               "config": {"address": "127.0.0.1", "username": "test"}}]
                             },
                            {"_id": "2", "name": "sub2", "is_active": True, "subscriber_type": SUBSCRIBER_TYPES.DIGITAL,
                             "media_type": "media", "sequence_num_settings": {"max": 10, "min": 1},
                             "email": "test@test.com",
                             "destinations": [{"name": "dest1", "format": "newsmlg2", "delivery_type": "ftp",
                                               "config": {"address": "127.0.0.1", "username": "test"}}]
                             }]

        self.articles = [{'guid': '1',
                          '_id': '1',
                          'last_version': 3,
                          config.VERSION: 4,
                          'body_html': "shouldn't be referenced by any package",
                          'urgency': 4,
                          'anpa_category': [{'qcode': 'A', 'name': 'Sport'}],
                          'headline': 'no package reference',
                          'pubstatus': 'usable',
                          'firstcreated': utcnow(),
                          'byline': 'By Alan Karben',
                          'dateline': {'located': {'city': 'Sydney'}},
                          'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          'expiry': utcnow() + timedelta(minutes=20),
                          ITEM_STATE: CONTENT_STATE.PROGRESS,
                          ITEM_TYPE: CONTENT_TYPE.TEXT,
                          'unique_name': '#1'},
                         {'guid': '2',
                          '_id': '2',
                          'last_version': 3,
                          config.VERSION: 4,
                          'body_html': 'some body',
                          'urgency': 4,
                          'headline': 'some headline',
                          'abstract': 'Abstract Sample',
                          'anpa_category': [{'qcode': 'A', 'name': 'Sport'}],
                          'pubstatus': 'done',
                          'firstcreated': utcnow(),
                          'byline': 'By Alan Karben',
                          'dateline': {'located': {'city': 'Sydney'}},
                          'slugline': 'taking takes',
                          'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          ITEM_STATE: CONTENT_STATE.PROGRESS,
                          'expiry': utcnow() + timedelta(minutes=20),
                          ITEM_TYPE: CONTENT_TYPE.TEXT,
                          'unique_name': '#2'},
                         {'guid': '3',
                          '_id': '3',
                          'last_version': 3,
                          config.VERSION: 4,
                          'body_html': 'some body',
                          'urgency': 4,
                          'headline': 'some headline',
                          'abstract': 'Abstract Sample',
                          'anpa_category': [{'qcode': 'A', 'name': 'Sport'}],
                          'pubstatus': 'done',
                          'firstcreated': utcnow(),
                          'byline': 'By Alan Karben',
                          'dateline': {'located': {'city': 'Sydney'}},
                          'slugline': 'taking takes',
                          'keywords': ['Student', 'Crime', 'Police', 'Missing'],
                          'subject': [{'qcode': '17004000', 'name': 'Statistics'},
                                      {'qcode': '04001002', 'name': 'Weather'}],
                          ITEM_STATE: CONTENT_STATE.PROGRESS,
                          'expiry': utcnow() + timedelta(minutes=20),
                          ITEM_TYPE: CONTENT_TYPE.TEXT,
                          'unique_name': '#3'},
                         {'guid': '4',
                          '_id': '4',
                          'headline': 'simple package with 2 items',
                          'last_version': 2,
                          config.VERSION: 3,
                          ITEM_TYPE: CONTENT_TYPE.COMPOSITE,
                          'groups': [{'id': 'root', 'refs': [{'idRef': 'main'}], 'role': 'grpRole:NEP'},
                                     {'id': 'main', 'role': 'grpRole:main',
                                      'refs': [
                                          {'location': ARCHIVE, 'guid': '2', ITEM_TYPE: CONTENT_TYPE.TEXT, RESIDREF: '2'
                                           },
                                          {'location': ARCHIVE, 'guid': '3', ITEM_TYPE: CONTENT_TYPE.TEXT, RESIDREF: '3'
                                           }]
                                      }],
                          'firstcreated': utcnow(),
                          'expiry': utcnow() + timedelta(minutes=20),
                          'unique_name': '#4',
                          ITEM_STATE: CONTENT_STATE.PROGRESS},
                         {'guid': '5',
                          '_id': '5',
                          'headline': 'package and item is also a package',
                          config.VERSION: 3,
                          ITEM_TYPE: CONTENT_TYPE.COMPOSITE,
                          'groups': [{'id': 'root', 'refs': [{'idRef': 'main'}], 'role': 'grpRole:NEP'},
                                     {'id': 'main', 'role': 'grpRole:main',
                                      'refs': [{'location': ARCHIVE, ITEM_TYPE: CONTENT_TYPE.COMPOSITE, RESIDREF: '4'}]
                                      }],
                          'firstcreated': utcnow(),
                          'expiry': utcnow() + timedelta(minutes=20),
                          'unique_name': '#5',
                          ITEM_STATE: CONTENT_STATE.PROGRESS}
                         ]

    def _create_and_insert_into_versions(self, item, insert_last_version_as_published):
        version = item[config.VERSION]
        archive_versions = []

        while version != 0:
            versioned_item = item.copy()
            versioned_item['_id_document'] = versioned_item['_id']
            versioned_item[config.VERSION] = version
            del versioned_item['_id']

            if insert_last_version_as_published and item[config.VERSION] == version:
                versioned_item[ITEM_STATE] = CONTENT_STATE.PUBLISHED

            archive_versions.append(versioned_item)
            version -= 1

        self.app.data.insert('archive_versions', archive_versions)

    def _get_legal_archive_details(self, article_id, publishing_action=None):
        archive_service = get_resource_service(LEGAL_ARCHIVE_NAME)
        archive_versions_service = get_resource_service(LEGAL_ARCHIVE_VERSIONS_NAME)
        publish_queue_service = get_resource_service(LEGAL_PUBLISH_QUEUE_NAME)

        article = archive_service.find_one(_id=article_id, req=None)
        resource_def = self.app.config['DOMAIN'][LEGAL_ARCHIVE_VERSIONS_NAME]
        version_id = versioned_id_field(resource_def)
        article_versions = archive_versions_service.get(req=None, lookup={version_id: article_id})

        lookup = {'item_id': article_id}
        if publishing_action:
            lookup['publishing_action'] = publishing_action

        queue_items = publish_queue_service.get(req=None, lookup=lookup)

        return article, article_versions, queue_items

    def _move_to_archived_and_assert_can_remove_from_production(self, item_id, assert_function, item_to_assert=None):
        published_service = get_resource_service(PUBLISHED)
        published_item = list(published_service.get_from_mongo(req=None, lookup={'item_id': item_id}))
        self.assertEqual(len(published_item), 1)

        # Moving to archived explicitly
        published_item = published_item[0]
        published_service.patch(id=published_item[config.ID_FIELD], updates={'allow_post_publish_actions': False})

        assert_function(published_service.can_remove_from_production(
            item_to_assert if item_to_assert else published_item))

        return published_item
