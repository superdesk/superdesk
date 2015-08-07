# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.metadata.item import ITEM_STATE

states = []
actions = []
allowed_workflow_states = []

__all__ = ['workflow_state', 'get_workflow_states', 'allowed_workflow_states',
           'workflow_action', 'get_workflow_actions', 'is_workflow_state_transition_valid',
           'set_default_state']


def workflow_action(name, include_states=None, exclude_states=None, privileges=None):
    """Register new workflow action.

    :param name: unique name of action
    :param include_states: include action if item state is in include_states
    :param exclude_states: exclude action if item state is in exclude_statese
    :param privileges: list of privileges required for this action
    """
    if include_states is None:
        include_states = []
    if exclude_states is None:
        exclude_states = []
    if privileges is None:
        privileges = []
    actions.append({
        'name': name,
        'exclude_states': exclude_states,
        'include_states': include_states,
        'privileges': privileges
    })


def get_workflow_actions(state=None):
    """Get list of all registered workflow actions.

    :param state: filter actions by given item state if provided
    """
    if state is None:
        return actions
    else:
        def is_go(action, state):
            if action['include_states']:
                return state in action['include_states']
            elif action['exclude_states']:
                return state not in action['exclude_states']
        return [action for action in actions if is_go(action, state)]


def get_privileged_actions(privileges):
    """ Get the actions that are within the privileged list
    :param privileges:
    :return: list of allowed actions
    """
    allowed_action = []
    for action in actions:
        # only add the action if it has some privileges
        add = len(action['privileges']) > 0
        for action_privilege in action['privileges']:
            if action_privilege not in privileges.keys():
                add = False
            else:
                # make sure the privilege is allowed
                if not privileges[action_privilege] == 1:
                    add = False
        if add:
            allowed_action.append(action)
    return allowed_action


def workflow_state(name):
    """Register new workflow state.

    :param name: unique name of state
    """
    allowed_workflow_states.append(name)
    states.append({'name': name})


def is_workflow_state_transition_valid(action_name, state):
    """
    Checks if the state transition is valid or not. It's assumed that there are no duplicate actions.

    :param action_name: Action Name as defined while registering Workflow Action.
    :param state: Current State of the content
    :return: true if valid, False otherwise.
    """
    return action_name in [action['name'] for action in get_workflow_actions(state)]


def get_workflow_states():
    """Get list of all registered workflow states."""
    return states


def set_default_state(doc, state):
    """Sets default state for given doc.

    :param doc: item
    :param state: state to be set as default
    """
    doc.setdefault(ITEM_STATE, state)
