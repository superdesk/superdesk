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
from superdesk.errors import SuperdeskApiError
from superdesk.services import BaseService


logger = logging.getLogger(__name__)


class KeywordsService(BaseService):
    """
    Analyze the text and extract the keywords
    """
    def __init__(self, datasource=None, backend=None):
        super().__init__(datasource, backend)
        self.provider = None

    def create(self, docs, **kwargs):
        if not self.provider:
            raise SuperdeskApiError.internalError('Not set a keywords provider')

        try:
            ids = []
            for doc in docs:
                doc['keywords'] = self.provider.get_keywords(doc.get('text', ''))
                ids.append(len(ids))
            return ids
        except Exception as ex:
            raise SuperdeskApiError.internalError(str(ex))
