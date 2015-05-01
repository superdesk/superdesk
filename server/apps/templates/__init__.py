# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from .content_templates import ContentTemplatesResource, ContentTemplatesService, CONTENT_TEMPLATE_PRIVILEGE
import superdesk


def init_app(app):
    endpoint_name = 'content_templates'
    service = ContentTemplatesService(endpoint_name, backend=superdesk.get_backend())
    ContentTemplatesResource(endpoint_name, app=app, service=service)

    superdesk.privilege(name=CONTENT_TEMPLATE_PRIVILEGE, label='Templates', description='Create templates')
