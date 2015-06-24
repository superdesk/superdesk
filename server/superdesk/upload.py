# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""Upload module"""
import logging
import superdesk
from eve.utils import config
from superdesk.errors import SuperdeskApiError
from werkzeug.wsgi import wrap_file
from .resource import Resource
from .services import BaseService
from flask import url_for, request, current_app as app
from superdesk.media.renditions import generate_renditions, delete_file_on_error
from superdesk.media.media_operations import download_file_from_url, process_file_from_stream, \
    crop_image, decode_metadata, download_file_from_encoded_str


bp = superdesk.Blueprint('upload_raw', __name__)
superdesk.blueprint(bp)
logger = logging.getLogger(__name__)
cache_for = 3600 * 24 * 30  # 30d cache


@bp.route('/upload/<path:media_id>/raw', methods=['GET'])
def get_upload_as_data_uri(media_id):
    media_file = app.media.get(media_id, 'upload')
    if media_file:
        data = wrap_file(request.environ, media_file, buffer_size=1024 * 256)
        response = app.response_class(
            data,
            mimetype=media_file.content_type,
            direct_passthrough=True)
        response.content_length = media_file.length
        response.last_modified = media_file.upload_date
        response.set_etag(media_file.md5)
        response.cache_control.max_age = cache_for
        response.cache_control.s_max_age = cache_for
        response.cache_control.public = True
        response.make_conditional(request)
        return response
    raise SuperdeskApiError.notFoundError('File not found on media storage.')


def url_for_media(media_id):
    try:
        return app.media.url_for_media(media_id)
    except AttributeError:
        return url_for('upload_raw.get_upload_as_data_uri', media_id=media_id,
                       _external=True, _schema=superdesk.config.URL_PROTOCOL)


def init_app(app):
    endpoint_name = 'upload'
    service = UploadService(endpoint_name, backend=superdesk.get_backend())
    UploadResource(endpoint_name, app=app, service=service)


class UploadResource(Resource):
    schema = {
        'media': {'type': 'file'},
        'CropLeft': {'type': 'integer'},
        'CropRight': {'type': 'integer'},
        'CropTop': {'type': 'integer'},
        'CropBottom': {'type': 'integer'},
        'URL': {'type': 'string'},
        'mime_type': {'type': 'string'},
        'filemeta': {'type': 'dict'}
    }
    extra_response_fields = ['renditions']
    datasource = {
        'projection': {
            'mime_type': 1,
            'filemeta': 1,
            '_created': 1,
            '_updated': 1,
            '_etag': 1,
            'media': 1,
            'renditions': 1,
        }
    }
    item_methods = ['GET', 'DELETE']
    resource_methods = ['GET', 'POST']
    privileges = {'POST': 'archive', 'DELETE': 'archive'}


class UploadService(BaseService):

    def on_create(self, docs):
        for doc in docs:
            if doc.get('URL') and doc.get('media'):
                message = 'Uploading file by URL and file stream in the same time is not supported.'
                raise SuperdeskApiError.badRequestError(message)

            content = None
            filename = None
            content_type = None
            if doc.get('media'):
                content = doc['media']
                filename = content.filename
                content_type = content.mimetype
            elif doc.get('URL'):
                content, filename, content_type = self.download_file(doc)

            self.store_file(doc, content, filename, content_type)

    def store_file(self, doc, content, filename, content_type):
        # retrieve file name and metadata from file
        file_name, content_type, metadata = process_file_from_stream(content, content_type=content_type)
        # crop the file if needed, can change the image size
        was_cropped, out = crop_image(content, filename, self.get_cropping_data(doc))
        # the length in metadata could be updated if it was cropped
        if was_cropped:
            file_name, content_type, metadata_after_cropped = process_file_from_stream(out, content_type=content_type)
            # when cropped, metadata are reseted. Then we update the previous metadata variable
            metadata['length'] = metadata_after_cropped['length']
        try:
            logger.debug('Going to save media file with %s ' % file_name)
            out.seek(0)
            file_id = app.media.put(out, filename=file_name, content_type=content_type,
                                    resource=self.datasource, metadata=metadata)
            doc['media'] = file_id
            doc['mime_type'] = content_type
            doc['filemeta'] = decode_metadata(metadata)
            inserted = [doc['media']]
            file_type = content_type.split('/')[0]
            rendition_spec = config.RENDITIONS['avatar']
            renditions = generate_renditions(out, doc['media'], inserted, file_type,
                                             content_type, rendition_spec, url_for_media)
            doc['renditions'] = renditions
        except Exception as io:
            logger.exception(io)
            for file_id in inserted:
                delete_file_on_error(doc, file_id)
            raise SuperdeskApiError.internalError('Generating renditions failed')

    def get_cropping_data(self, doc):
        if all([doc.get('CropTop', None) is not None, doc.get('CropLeft', None) is not None,
                doc.get('CropRight', None) is not None, doc.get('CropBottom', None) is not None]):
            cropping_data = (doc['CropLeft'], doc['CropTop'], doc['CropRight'], doc['CropBottom'])
            return cropping_data
        return None

    def download_file(self, doc):
        url = doc.get('URL')
        if not url:
            return
        if url.startswith('data'):
            return download_file_from_encoded_str(url)
        else:
            return download_file_from_url(url)
