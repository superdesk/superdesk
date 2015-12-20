# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from .commands import LegalArchiveImport
from test_factory import SuperdeskTestCase


class LegalArchiveTestCase(SuperdeskTestCase):

    desks = [{'_id': '123', 'name': 'Sports'}]
    users = [{'_id': '123', 'username': 'test1', 'first_name': 'test', 'last_name': 'user', 'email': 'a@a.com'}]
    stages = [{'_id': '123', 'name': 'working stage', 'desk': '123'}]
    archive = [
        {
            'task': {'desk': '123', 'stage': '123'}
        },
        {
            'task': {'desk': '1234', 'stage': None, 'user': '123'}
        },
        {
            'task': {'desk': '1234', 'stage': 'dddd', 'user': 'test'}
        }
    ]

    def setUp(self):
        super().setUp()
        self.app.data.insert("desks", self.desks)
        self.app.data.insert("users", self.users)
        self.app.data.insert("stages", self.stages)

    def test_denormalize_desk_user(self):
        LegalArchiveImport()._denormalize_user_desk(self.archive[0], '')
        task = self.archive[0]['task']
        self.assertEqual(task.get('desk'), 'Sports')
        self.assertEqual(task.get('stage'), 'working stage')
        self.assertEqual(task.get('user'), '')

    def test_denormalize_not_configured_desk(self):
        LegalArchiveImport()._denormalize_user_desk(self.archive[1], '')
        task = self.archive[1]['task']
        self.assertEqual(task.get('desk'), '1234')
        self.assertEqual(task.get('stage'), None)
        self.assertEqual(task.get('user'), 'test user')

    def test_denormalize_not_configured_desk_stage_user(self):
        LegalArchiveImport()._denormalize_user_desk(self.archive[2], '')
        task = self.archive[2]['task']
        self.assertEqual(task.get('desk'), '1234')
        self.assertEqual(task.get('stage'), 'dddd')
        self.assertEqual(task.get('user'), '')
