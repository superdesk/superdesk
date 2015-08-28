# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import apps.io.aap  # NOQA
import apps.io.afp  # NOQA
import apps.io.dpa  # NOQA
import apps.io.reuters  # NOQA

from superdesk.io import register_provider


register_provider('search', None, [])
