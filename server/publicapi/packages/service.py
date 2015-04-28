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
