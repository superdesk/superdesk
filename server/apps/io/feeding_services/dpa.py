# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license*.


import logging

from macros.dpa_derive_dateline import dpa_derive_dateline
from superdesk.io import register_feeding_service
from superdesk.io.feeding_services.file_service import FileFeedingService

logger = logging.getLogger(__name__)


class DPAFileFeedingService(FileFeedingService):
    """
    Feeding Service class which can read article(s) from file system provided by DPA.
    """

    NAME = 'dpa_file'

    def _update(self, provider):
        super()._update(provider)

    def after_extracting(self, article, provider):
        dpa_derive_dateline(article)


register_feeding_service(DPAFileFeedingService.NAME, DPAFileFeedingService(), FileFeedingService.ERRORS)
