
import superdesk

from superdesk import tests


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

        superdesk.workflow_action(
            name='exclude',
            exclude_states=['exclude'],
        )

        actions = [action for action in superdesk.get_workflow_actions() if action['name'] == 'include']
        self.assertEqual(1, len(actions))
        self.assertIn('include', actions[0]['include_states'])
        self.assertIn('test-privilege', actions[0]['privileges'])

        self.assertActionIn('include', superdesk.get_workflow_actions(state='include'))
        self.assertActionIn('exclude', superdesk.get_workflow_actions(state='other'))
        self.assertActionIn('exclude', superdesk.get_workflow_actions(state='include'))

    def assertActionIn(self, action, actions):
        self.assertIn(action, [a['name'] for a in actions])
