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
                media_file.metadata[k] = json.loads(v)
        return media_file

    def put(self, content, filename=None, content_type=None, metadata=None):
        _id = self.fs().put(content, content_type=content_type, filename=filename, metadata=metadata)
        logger.debug('Saved  media file with id= %s' % _id)
        return _id

    def fs(self):
        if self._fs is None:
            self._fs = GridFS(self.app.data.mongo.driver.db)
        return self._fs
