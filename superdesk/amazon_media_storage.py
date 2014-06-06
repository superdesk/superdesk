''' Amazon media storage module'''
from eve.io.media import MediaStorage
import tinys3
from superdesk.media_operations import process_file_from_stream
from superdesk import SuperdeskError
import logging
from io import BytesIO

logger = logging.getLogger(__name__)


class AmazonObjectWrapper():

    def __init__(self, stream_generator, content_type, length, name, metadata):
        self.stream_gen = stream_generator
        self.content_type = content_type
        self.length = int(length)
        self.name = name
        self.metadata = metadata

    def read(self):
        out = BytesIO()
        for bytes in self.stream_gen:
            out.write(bytes)
        out.seek(0)
        return out.read()

    def __repr__(self):
        return ('[AmazonObjectWrapper name=%s content_type=%s length=%s metadata=%s]' % self.name,
                self.content_type, self.length, self.metadata)


class AmazonMediaStorage(MediaStorage):

    def __init__(self, app=None):
        super().__init__(app)
        if 'AMAZON_REGION' in app.config:
            region = app.config['AMAZON_REGION']
        else:
            region = 's3'
        username = self.app.config['AMAZON_ACCESS_KEY_ID']
        api_key = self.app.config['AMAZON_SECRET_ACCESS_KEY']
        self.container_name = self.app.config['AMAZON_CONTAINER_NAME']
        endpoint = '%s.amazonaws.com' % region
        self.conn = tinys3.Connection(username, api_key, tls=True, endpoint=endpoint)

    def get(self, id_or_filename):
        """ Opens the file given by name or unique id. Note that although the
        returned file is guaranteed to be a File object, it might actually be
        some subclass. Returns None if no file was found.
        """
        id_or_filename = str(id_or_filename)
        found, obj = self._check_exists(id_or_filename)
        if found:
            return AmazonObjectWrapper(obj, obj.headers['content-type'], obj.headers['content-length'], id_or_filename,
                                       {})
        return None

    def put(self, content, filename=None, content_type=None):
        """ Saves a new file using the storage system, preferably with the name
        specified. If there already exists a file with this name name, the
        storage system may modify the filename as necessary to get a unique
        name. Depending on the storage system, a unique id or the actual name
        of the stored file will be returned. The content type argument is used
        to appropriately identify the file when it is retrieved.
        """
        file_name, iter_content, content_type, metadata = process_file_from_stream(content, filename, content_type)
        logger.debug('Going to save media file with %s ' % file_name)
        found, existing_file = self._check_exists(file_name)
        if found:
            return file_name

        try:
            res = self.conn.upload(file_name, iter_content, self.container_name, content_type=content_type)
            if res.status_code not in (200, 201):
                raise SuperdeskError(payload='Uploading file to amazon S3 failed')
            return file_name
        except Exception as ex:
            logger.exception(ex)
            raise

    def delete(self, id_or_filename):
        id_or_filename = str(id_or_filename)
        del_res = self.conn.delete(id_or_filename, self.container_name)
        logger.debug('Amazon S3 file deleted %s with status' % id_or_filename, del_res.status_code)

    def exists(self, id_or_filename):
        """ Returns True if a file referenced by the given name or unique id
        already exists in the storage system, or False if the name is available
        for a new file.
        """
        id_or_filename = str(id_or_filename)
        found, _ = self._check_exists(id_or_filename)
        return found

    def _check_exists(self, id_or_filename):
        try:
            obj = self.conn.get(id_or_filename, self.container_name)
            if obj.status_code not in (200, 201):
                message = 'Retrieving file %s from amazon failed' % id_or_filename
                raise SuperdeskError(payload=message)
            return (True, obj)
        except Exception as ex:
            logger.exception(ex)
            # File not found
            return (False, None)
