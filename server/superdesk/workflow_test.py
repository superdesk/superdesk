# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import superdesk

from superdesk import tests


def names(actions):
    return [a['name'] for a in actions]


class WorkflowTestCase(tests.TestCase):

    def test_status_registry(self):
        superdesk.workflow_state(name='test')
        self.assertIn({'name': 'test'}, superdesk.get_workflow_states())
        self.assertIn('test', superdesk.allowed_workflow_states)

    def test_action_registry(self):
        superdesk.workflow_action(
            name='include',
            include_states=['include'],
            privileges=['test-privilege']
        )

        actions = [action for action in superdesk.get_workflow_actions() if action['name'] == 'include']
        self.assertEqual(1, len(actions))
        self.assertIn('include', actions[0]['include_states'])
        self.assertIn('test-privilege', actions[0]['privileges'])

        self.assertIn('spike', names(superdesk.get_workflow_actions(state='draft')))
        self.assertNotIn('spike', names(superdesk.get_workflow_actions(state='spiked')))
        self.assertIn('unspike', names(superdesk.get_workflow_actions(state='spiked')))
        self.assertNotIn('unspike', names(superdesk.get_workflow_actions(state='draft')))

    def test_is_workflow_action_valid(self):
        superdesk.workflow_action(
            name='test_spike',
            exclude_states=['spiked', 'published', 'scheduled', 'killed'],
            privileges=['spike']
        )

        superdesk.workflow_action(
            name='test_on_hold',
            exclude_states=['spiked', 'published', 'scheduled', 'killed', 'on_hold'],
            privileges=['on_hold']
        )

        self.assertTrue(superdesk.is_workflow_state_transition_valid('test_spike', 'in_progress'))
        self.assertFalse(superdesk.is_workflow_state_transition_valid('test_spike', 'spiked'))
        self.assertTrue(superdesk.is_workflow_state_transition_valid('test_on_hold', 'routed'))
        self.assertTrue(superdesk.is_workflow_state_transition_valid('test_on_hold', 'fetched'))
        self.assertFalse(superdesk.is_workflow_state_transition_valid('test_on_hold', 'published'))
        self.assertFalse(superdesk.is_workflow_state_transition_valid('test_on_hold', 'scheduled'))
