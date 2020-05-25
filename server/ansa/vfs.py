
import io
import os
import time
import arrow
import random
import hashlib
import logging
import requests
import tempfile

from lxml import etree
from urllib.parse import urljoin
from flask import current_app as app, json
from eve.io.media import MediaStorage
from superdesk.errors import SuperdeskError

UPLOAD_ENDPOINT = '/bdmvfs/rest/uploadfile'
BINARY_ENDPOINT = '/bdmvfs/rest/binfilebymd5/%s'
METADATA_ENDPOINT = '/bdmvfs/rest/infofilebymd5/%s'
DELETE_ENDPOINT = '/bdmvfs/rest/deletefilebymd5/%s'
PUT_METADATA_ENDPOINT = '/bdmvfs/rest/uploadfilemeta'

logger = logging.getLogger(__name__)

TIMEOUT = (5, 15)
DOWNLOAD_TIMEOUT = (5, 30)

UPLOAD_RETRY = 3


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


def parse_xml(resp, allow_error=False):
    resp.raise_for_status()
    assert resp.status_code in [200, 201], resp
    logger.debug('vfs %s', resp.content.decode('utf-8'))
    xml = etree.fromstring(resp.content)
    if is_error(xml) and not allow_error:
        errors = xml.find('errors')
        raise VFSError(errors.find('message').text)
    return xml


def is_error(xml):
    try:
        return bool(xml.find('errors').find('code').text)
    except AttributeError:
        return False


class VFSMediaStorage(MediaStorage):

    def __init__(self, app=None):
        super().__init__(app)
        self._sess = requests.Session()

    def url(self, endpoint):
        return urljoin(app.config.get('ANSA_VFS', 'http://172.20.14.95:8080/'), endpoint)

    def get(self, id_or_filename, resource=None):
        resp = self._sess.get(self.url(BINARY_ENDPOINT) % id_or_filename, timeout=DOWNLOAD_TIMEOUT)
        if resp.status_code in [200, 201]:
            metadata = self.metadata(id_or_filename, resource, ignore_error=True)
            return VFSObjectWrapper(id_or_filename, resp.content, metadata)

    def exists(self, id_or_filename, resource=None):
        try:
            return bool(self.metadata(id_or_filename, resource))
        except VFSError:
            return False

    def delete(self, id_or_filename, resource=None):
        resp = self._sess.delete(self.url(DELETE_ENDPOINT) % id_or_filename, timeout=TIMEOUT)
        xml = parse_xml(resp, allow_error=True)
        try:
            specific = xml.find('errors').find('specific').text
            if 'File to delete not found' in specific:
                logger.warning('File was removed already from vfs md5=%s', id_or_filename)
        except AttributeError:
            pass
        return is_error(xml)

    def metadata(self, id_or_filename, resource=None, ignore_error=False):
        resp = self._sess.get(self.url(METADATA_ENDPOINT) % id_or_filename, timeout=TIMEOUT)
        try:
            xml = parse_xml(resp)
        except VFSError:
            if not ignore_error:
                raise
            return {}
        if is_error(xml):
            return {}
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
        content.seek(0, os.SEEK_END)
        length = content.tell()
        content.seek(0)
        assert length, 'filename {} is empty'.format(filename)

        md5_test = hashlib.md5(content.read()).hexdigest()

        for i in range(UPLOAD_RETRY):
            content.seek(0)
            files = {'file': content}
            resp = self._sess.post(self.url(UPLOAD_ENDPOINT), files=files, data={'commit': 'true'},
                                   timeout=DOWNLOAD_TIMEOUT)
            md5 = _get_md5(resp)
            if md5_test == md5:
                logger.info('put %s md5=%s size=%d retry=%d', filename, md5, length, i)
                return md5

            if i + 1 < UPLOAD_RETRY:
                logger.warning('md5 from vfs does not match, retry vfs=%s local=%s filename=%s size=%d',
                               md5, md5_test, filename, length)
                time.sleep(random.random())

        with tempfile.NamedTemporaryFile(prefix=filename, delete=False) as output:
            content.seek(0)
            output.write(content.read())
            raise VFSError('put error filename={} tmpfile={} size={}'.format(filename, output.name, length))

    def put_metadata(self, media, metadata):
        data = {
            'md5': str(media),
            'meta': metadata,
        }
        logger.info('put metadata %s', json.dumps(data))
        resp = self._sess.post(self.url(PUT_METADATA_ENDPOINT), json=data, timeout=TIMEOUT)
        md5 = _get_md5(resp)
        logger.info('updated metadata old=%s new=%s', str(media), str(md5))
        return md5

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


def _get_md5(resp):
    xml = parse_xml(resp)
    md5 = xml.find('fileItems').find('md5')
    if md5 is not None:
        return md5.text
