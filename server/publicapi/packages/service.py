# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from publicapi.items.service import ItemsService


logger = logging.getLogger(__name__)


class PackagesService(ItemsService):
    """
    A service that knows how to perform CRUD operations on the `package`
    content types.

    Serves mainly as a proxy to the data layer.
    """

    def on_fetched_item(self, document):
        """Event handler when a single package is retrieved from database.

        It sets the `uri` field for all associated (referenced) objects.

        :param dict document: fetched MongoDB document representing the package
        """
        self._process_referenced_objects(document)
        super().on_fetched_item(document)

    def on_fetched(self, result):
        """Event handler when a collection of packages is retrieved from
        database.

        For each package in the fetched collection it sets the `uri` field for
        all objects associated with (referenced by) the package.

        :param dict result: dictionary contaning the list of MongoDB documents
            (the fetched packages) and some metadata, e.g. pagination info
        """
        for document in result['_items']:
            self._process_referenced_objects(document)
        super().on_fetched(result)

    def _process_referenced_objects(self, document):
        """Do some processing on the objects referenced by `document`.

        For all referenced objects their `uri` field is generated and their
        `_id` field removed.

        :param dict document: MongoDB document representing a package object
        """
        for name, target_obj in document.get('associations', {}).items():
            target_obj['uri'] = self._get_uri(target_obj)
            del target_obj['_id']
