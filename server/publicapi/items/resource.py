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

# admin metadata
# uri, representationtype, profile, embargoed, copyrightholder, copyrightnotice
# type, mimetype, version, versioncreated, pubstatus, usageterms

# desc metadata
# person, organisation, event, object, geometry_
# language, place, subject, urgency

# content
# body_xhtml, description_text, description_xhtml
# byline, located, headline, body_text, renditions


class ItemsResource(Resource):
    '''
    Dictionaries schema
    '''
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
        'filter': {'type': 'text'},
#         'search_backend': 'elastic',
    }
    item_methods = ['GET']
    resource_methods = ['GET']
