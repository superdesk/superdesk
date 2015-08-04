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
from .workspace import WorkspaceService, WorkspaceResource


def init_app(app):
    superdesk.register_resource('workspaces', WorkspaceResource, WorkspaceService,
                                privilege=['POST', 'PATCH', 'DELETE'])
    superdesk.register_default_user_preference('workspace:active', {
        'type': 'string',
        'workspace': ''
    })
