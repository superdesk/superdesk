
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
