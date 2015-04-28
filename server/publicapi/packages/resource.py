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


class PackagesResource(Resource):
    """A class defining and configuring the /packages API endpoint."""

    # Example of an ID of an object in database (whitout quotes):
    #
    #   "tag:example.com,0000:newsml_BRE9A605"
    #
    item_url = 'regex("[\w,.:-]+")'

    schema = {
        'guid': {'type': 'string'},
        'type': {'type': 'string'},
        'unique_id': {'type': 'integer'},
        'unique_name': {'type': 'string'},
        'pubstatus': {'type': 'string'},
        'firstcreated': {'type': 'datetime'},
        'versioncreated': {'type': 'datetime'},
        'original_creator': {'type': 'string'},
        'version_creator': {'type': 'string'},
        'groups': {'type': 'list'},
        'language': {'type': 'string'},
        'headline': {'type': 'string'},
        'slugline': {'type': 'string'},
        'description': {'type': 'string'},
    }

    datasource = {
        'filter': {'type': 'composite'},
        'source': 'items',
        'projection': {
            '_created': 0,
            '_updated': 0,
        }
    }

    item_methods = ['GET']
    resource_methods = ['GET']
