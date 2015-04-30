# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os
import superdesk
from superdesk.utils import ListCursor

__templates__ = [('kill', 'templates/kill_article.json')]

class TemplatesService(superdesk.Service):

    def get(self, req, lookup):
        templates = []
        current_path = os.path.realpath(os.path.dirname(__file__))
        for (name, path) in __templates__:
            template_path = os.path.join(current_path, path)
            with open(template_path) as data_file:
                data = superdesk.json.load(data_file)
                templates.append({'name': name, 'template': data})
        print('Got templates:', templates)
        return ListCursor(templates)


class TemplatesResource(superdesk.Resource):
    resource_methods = ['GET']
    item_methods = []

    schema = {
        'name': {
            'type': 'string',
            'required': True
        },
        'template': {
            'type': 'dict',
        }
    }


def init_app(app):
    TemplatesResource('templates', app=app, service=TemplatesService())
