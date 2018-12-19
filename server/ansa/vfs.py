
import io
import arrow
import logging
import requests

from lxml import etree
from urllib.parse import urljoin
from flask import current_app as app
from eve.io.media import MediaStorage
from superdesk.errors import SuperdeskError

UPLOAD_ENDPOINT = '/bdmvfs/rest/uploadfile'
BINARY_ENDPOINT = '/bdmvfs/rest/binfilebymd5/%s'
METADATA_ENDPOINT = '/bdmvfs/rest/infofilebymd5/%s'
DELETE_ENDPOINT = '/bdmvfs/rest/deletefilebymd5/%s'

logger = logging.getLogger(__name__)


class VFSError(SuperdeskError):
    pass


class VFSObjectWrapper(io.BytesIO):

    def __init__(self, _id, content, metadata):
        self._id = _id
        self.md5 = metadata.get('md5', _id)
        self.name = metadata.get('filename')
        self.filename = metadata.get('filename')
        self.length = metadata.get('length')
        self.content_type = metadata.get('mimetype')
        self.upload_date = metadata.get('created')

        # store content
        self.write(content)
        self.seek(0)


def parse_xml(resp):
    assert resp.status_code in [200, 201]
    logger.debug('vfs %s', resp.content.decode('utf-8'))
    xml = etree.fromstring(resp.content)
    if is_error(xml):
        errors = xml.find('errors')
        raise VFSError(errors.find('message').text)
    return xml


def is_error(xml):
    try:
        return bool(xml.find('errors').find('code').text)
    except AttributeError:
        return False


class VFSMediaStorage(MediaStorage):

    def url(self, endpoint):
        return urljoin(app.config.get('VFS_URL', 'http://172.20.14.95:8080/'), endpoint)

    def get(self, id_or_filename, resource=None):
        resp = requests.get(self.url(BINARY_ENDPOINT) % id_or_filename)
        if resp.status_code in [200, 201]:
            metadata = self.metadata(id_or_filename, resource)
            return VFSObjectWrapper(id_or_filename, resp.content, metadata)

    def exists(self, id_or_filename, resource=None):
        try:
            return bool(self.metadata(id_or_filename, resource))
        except VFSError:
            return False

    def delete(self, id_or_filename, resource=None):
        resp = requests.delete(self.url(DELETE_ENDPOINT) % id_or_filename)
        return parse_xml(resp)

    def metadata(self, id_or_filename, resource=None):
        resp = requests.get(self.url(METADATA_ENDPOINT) % id_or_filename)
        xml = parse_xml(resp)
        if is_error(xml):
            return None
        item = xml.find('fileItems')
        if item is None:
            return {}
        return {
            'md5': item.find('md5').text,
            'length': int(item.find('fsize').text),
            'mimetype': item.find('mimetype').text,
            'filename': item.find('filename').text,
            'created': arrow.get(item.find('created').text).datetime,
        }

    def put(self, content, filename=None, content_type=None, *args, **kwargs):
        files = {'file': content}
        resp = requests.post(self.url(UPLOAD_ENDPOINT), files=files)
        xml = parse_xml(resp)
        md5 = xml.find('fileItems').find('md5')
        if md5 is not None:
            return md5.text

    def url_for_media(self, media, content_type=None):
        return self.url(BINARY_ENDPOINT) % media

    def url_for_download(self, media, content_type=None):
        return self.app.download_url(media)

    def getFilename(self, media):
        return self.metadata(media).get('filename')

    def remove_unreferenced_files(self, existing_files, resource=None):
        pass

    def fetch_rendition(self, rendition, resource=None):
        return self.get(rendition['media'], resource)
