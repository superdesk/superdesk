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

    def get(self, _id, resource):
        logger.debug('Getting media file with id= %s' % _id)
        if isinstance(_id, str):
            _id = ObjectId(_id)
        media_file = super().get(_id, resource)
        if media_file and media_file.metadata:
            for k, v in media_file.metadata.items():
                try:
                    if isinstance(v, str):
                        media_file.metadata[k] = json.loads(v)
                except ValueError:
                    logger.exception('Failed to load metadata for file: %s with key: %s and value: %s', _id, k, v)

        return media_file

    def put(self, content, filename=None, content_type=None, metadata=None, resource=None, **kwargs):
        _id = self.fs(resource).put(content, content_type=content_type, filename=filename, metadata=metadata, **kwargs)
        return _id

    def fs(self, resource):
        resource = resource or 'upload'
        driver = self.app.data.mongo
        px = driver.current_mongo_prefix(resource)
        if px not in self._fs:
            self._fs[px] = GridFS(driver.pymongo(prefix=px).db)
        return self._fs[px]
