# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging

logging.basicConfig(handlers=[logging.StreamHandler()])
logger = logging.getLogger('superdesk')
logger.setLevel(logging.INFO)


def item_msg(msg, item):
    """Return a message with item id appended.

    :param msg: Original message
    :param item: Item object
    """
    return '{} item={}'.format(msg, str(item.get('_id', item.get('guid'))))
