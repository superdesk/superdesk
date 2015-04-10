#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


MONGO_DBNAME = 'superdesk'  # XXX: read from superdesk settings?

DOMAIN = {

    # TODO: add endpoint for packages (type: composite)

    'items': {
        'item_url': 'regex("(\w|[:-])+")',  # XXX: set globally! ITEM_URL

        'datasource': {
            'source': 'archive'  # TODO:des not work!
        }
    },

    # we need this so that the archive collection is accessible from
    # other (public) API endpoints
    # XXX: is it possible to somehow get rid of this?
    'archive': {
        'internal_resource': True
    }
}
