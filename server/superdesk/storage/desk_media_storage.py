# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from eve.io.mongo.media import GridFSMediaStorage
import logging
import json
from bson import ObjectId
from gridfs import GridFS


logger = logging.getLogger(__name__)


class SuperdeskGridFSMediaStorage(GridFSMediaStorage):

    def get(self, _id):
        logger.debug('Getting media file with id= %s' % _id)
        if isinstance(_id, str):
            _id = ObjectId(_id)
        media_file = super().get(_id)
        if media_file and media_file.metadata:
            for k, v in media_file.metadata.items():
                try:
                    media_file.metadata[k] = json.loads(v)
                except ValueError:
                    logger.exception('Failed to load metadata for file: %s with key: %s and value: %s', _id, k, v)

        return media_file

    def put(self, content, filename=None, content_type=None, metadata=None):
        _id = self.fs().put(content, content_type=content_type, filename=filename, metadata=metadata)
        return _id

    def fs(self):
        driver = self.app.data.mongo
        px = driver.current_mongo_prefix()
        if px not in self._fs:
            self._fs[px] = GridFS(driver.pymongo(prefix=px).db)
        return self._fs[px]
