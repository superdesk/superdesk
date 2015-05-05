# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.resource import Resource


class ItemsResource(Resource):
    """A class defining and configuring the /items API endpoint."""

    # Example of an ID of an object in database (whitout quotes):
    #
    #     "tag:example.com,0000:newsml_BRE9A605"
    #     "tag:localhost:2015:f4b35e12-559b-4a2b-b1f2-d5e64048bde8"
    #
    item_url = 'regex("[\w,.:-]+")'

    schema = {
        'guid': {'type': 'string'},
        'type': {'type': 'string'},
        'mimetype': {'type': 'string'},
        'version': {'type': 'integer'},
        'versioncreated': {'type': 'datetime'},
        'pubstatus': {'type': 'string'},
        'usageterms': {'type': 'string'},
        'language': {'type': 'string'},
        'place': {'type': 'list'},
        'subject': {'type': 'string'},
        'urgency': {'type': 'integer'},
        'byline': {'type': 'string'},
        'located': {'type': 'string'},
        'headline': {'type': 'string'},
        'body_text': {'type': 'string'},
        'renditions': {'type': 'dict'},
    }
    datasource = {
        'filter': {'type': {'$ne': 'composite'}},
        'projection': {
            '_created': 0,
            '_updated': 0,
        }
    }
    item_methods = ['GET']
    resource_methods = ['GET']
