"""Upload module"""
import logging
import superdesk
from eve.utils import config
from superdesk import SuperdeskError
from .models import BaseModel
from flask import url_for, Response, current_app as app, json
from superdesk.media.renditions import generate_renditions, delete_file_on_error
from superdesk.media.media_operations import download_file_from_url, process_file_from_stream, \
    crop_image, decode_metadata

bp = superdesk.Blueprint('upload_raw', __name__)
superdesk.blueprint(bp)
logger = logging.getLogger(__name__)


@bp.route('/upload/<path:media_id>/raw', methods=['GET'])
def get_upload_as_data_uri(media_id):
    media_file = app.media.get(media_id)
    if media_file:
        return Response(media_file.read(), mimetype=media_file.content_type)
    raise SuperdeskError(status_code=404, payload='File not found on media storage.')


def url_for_media(media_id):
    return url_for('upload_raw.get_upload_as_data_uri', media_id=media_id,
                   _external=True, _schema=superdesk.config.URL_PROTOCOL)


def init_app(app):
    UploadModel(app=app)


class UploadModel(BaseModel):
    endpoint_name = 'upload'
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
            'media': 1,
            'renditions': 1,
        }
    }
    item_methods = ['GET', 'DELETE']
    resource_methods = ['GET', 'POST']

    def on_create(self, docs):
        for doc in docs:
            if doc.get('URL') and doc.get('media'):
                message = 'Uploading file by URL and file stream in the same time is not supported.'
                raise SuperdeskError(payload=message)

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
        res = process_file_from_stream(content, filename=filename, content_type=content_type)
        file_name, content_type, metadata = res

        cropping_data = self.get_cropping_data(doc)
        _, out = crop_image(content, filename, cropping_data)
        metadata['length'] = json.dumps(len(out.getvalue()))

        try:
            logger.debug('Going to save media file with %s ' % file_name)
            out.seek(0)
            id = app.media.put(out, filename=file_name, content_type=content_type, metadata=metadata)
            doc['media'] = id
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
            raise SuperdeskError(message='Generating renditions failed')

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
        return download_file_from_url(url)
