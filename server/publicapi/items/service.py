# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from flask import current_app as app
import logging
from urllib.parse import urljoin, quote

from superdesk.services import BaseService


logger = logging.getLogger(__name__)


class ItemsService(BaseService):
    """
    A service that knows how to perform CRUD operations on the `item`
    content types.

    Serves mainly as a proxy to the data layer.
    """

    def _set_uri(self, doc):
        resource_url = app.config['PUBLICAPI_URL'] + '/' + app.config['URLS'][self.datasource] + '/'
        doc['uri'] = urljoin(resource_url, quote(doc['_id']))

    def on_fetched_item(self, doc):
        self._set_uri(doc)

    def on_fetched(self, res):
        for doc in res['_items']:
            self._set_uri(doc)
        return res
