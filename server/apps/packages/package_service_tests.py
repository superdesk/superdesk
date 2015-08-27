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
from .package_service import PackageService


class PackageServiceTestCase(SuperdeskTestCase):

    def setUp(self):
        super().setUp()
        self.package1 = {"groups": [{"id": "root",
                                     "refs": [
                                         {
                                             "idRef": "main"
                                         },
                                         {
                                             "idRef": "sidebars"
                                         }
                                     ],
                                     "role": "grpRole:NEP"
                                     },
                                    {
                                    "id": "main",
                                    "refs": [
                                        {
                                            "renditions": {},
                                            "slugline": "Take-1 slugline",
                                            "guid": "123",
                                            "headline": "Take-1 soccer headline",
                                            "location": "archive",
                                            "type": "text",
                                            "itemClass": "icls:text",
                                            "residRef": "123"
                                        },
                                        {
                                            "renditions": {},
                                            "slugline": "Take-3 slugline",
                                            "guid": "789",
                                            "headline": "Take-3 soccer headline",
                                            "location": "archive",
                                            "type": "text",
                                            "itemClass": "icls:text",
                                            "residRef": "789"
                                        }
                                    ],
                                    "role": "grpRole:main"
                                    },
                                    {
                                    "id": "sidebars",
                                    "refs": [
                                        {
                                            "renditions": {},
                                            "slugline": "Take-2 slugline",
                                            "guid": "456",
                                            "headline": "Take-2 soccer headline",
                                            "location": "archive",
                                            "type": "text",
                                            "itemClass": "icls:text",
                                            "residRef": "456"
                                        }
                                    ],
                                    "role": "grpRole:sidebars"
                                    }]}

    def test_remove_ref_from_package(self):
        with self.app.app_context():
            anything_left = PackageService().remove_ref_from_inmem_package(self.package1, "456")
            self.assertEqual(len(self.package1.get('groups', [])), 2)
            root_group = self.package1.get('groups', [])[0]
            self.assertEqual(len(root_group.get('refs', [])), 1)
            self.assertTrue(anything_left)

    def test_remove_two_refs_from_package(self):
        anything_left1 = PackageService().remove_ref_from_inmem_package(self.package1, "456")
        anything_left2 = PackageService().remove_ref_from_inmem_package(self.package1, "123")
        self.assertEqual(len(self.package1.get('groups', [])), 2)
        root_group = self.package1.get('groups', [])[0]
        self.assertEqual(len(root_group.get('refs', [])), 1)
        self.assertTrue(anything_left1)
        self.assertTrue(anything_left2)

    def test_remove_two_refs_from_package2(self):
        PackageService().remove_ref_from_inmem_package(self.package1, "789")
        PackageService().remove_ref_from_inmem_package(self.package1, "123")
        self.assertEqual(len(self.package1.get('groups', [])), 2)
        root_group = self.package1.get('groups', [])[0]
        self.assertEqual(len(root_group.get('refs', [])), 1)

    def test_remove_all_refs_from_package(self):
        anything_left1 = PackageService().remove_ref_from_inmem_package(self.package1, "456")
        anything_left2 = PackageService().remove_ref_from_inmem_package(self.package1, "789")
        anything_left3 = PackageService().remove_ref_from_inmem_package(self.package1, "123")
        self.assertEqual(len(self.package1.get('groups', [])), 1)
        root_group = self.package1.get('groups', [])[0]
        self.assertEqual(len(root_group.get('refs', [])), 0)
        self.assertTrue(anything_left1)
        self.assertTrue(anything_left2)
        self.assertFalse(anything_left3)
