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
        'associations': {'type': 'dict'},
        'body_html': {'type': 'string'},
        'body_text': {'type': 'string'},
        'byline': {'type': 'string'},
        'copyrightnotice': {'type': 'string'},
        'description_html': {'type': 'string'},
        'description_text': {'type': 'string'},
        'headline': {'type': 'string'},
        'language': {'type': 'string'},
        'located': {'type': 'string'},
        'mimetype': {'type': 'string'},
        'organization': {'type': 'list'},
        'person': {'type': 'list'},
        'place': {'type': 'list'},
        'profile': {'type': 'string'},
        'pubstatus': {'type': 'string'},
        'renditions': {'type': 'dict'},
        'subject': {'type': 'list'},
        'type': {'type': 'string'},
        'urgency': {'type': 'integer'},
        'uri': {'type': 'string'},
        'usageterms': {'type': 'string'},
        'version': {'type': 'string'},
        'versioncreated': {'type': 'datetime'},
    }

    datasource = {
        'search_backend': 'elastic',
        'elastic_filter': {"bool": {"must_not": {"term": {"type": "composite"}}}},
        'default_sort': [('_updated', -1)],
    }

    item_methods = ['GET']
    resource_methods = ['GET']
