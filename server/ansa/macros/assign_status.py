# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013-2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from eve.utils import config
from superdesk import get_resource_service
from planning.common import ASSIGNMENT_WORKFLOW_STATE
from copy import deepcopy


def update_on_assign_id(item, **kwargs):
    assign_id = item.get('assignment_id')
    if assign_id:
        assignments_service = get_resource_service('assignments')
        assignment = assignments_service.find_one(req=None, _id=assign_id)
        if assignment is None:
            return item
        if assignment['assigned_to']['state'] == ASSIGNMENT_WORKFLOW_STATE.ASSIGNED:
            updates = {'assigned_to': deepcopy(assignment.get('assigned_to'))}
            updates['assigned_to']['state'] = ASSIGNMENT_WORKFLOW_STATE.IN_PROGRESS
            assignments_service.patch(assignment[config.ID_FIELD], updates)
    return item


name = 'assign_status'
label = 'Update Status On Assignment ID'
callback = update_on_assign_id
access_type = 'backend'
action_type = 'direct'
