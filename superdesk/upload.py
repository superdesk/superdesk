"""Upload module"""

import superdesk
from superdesk import SuperdeskError
from superdesk.base_view_controller import BaseViewController
from flask import url_for, Response
from .media_operations import store_file_from_url

bp = superdesk.Blueprint('upload', __name__)
superdesk.blueprint(bp)


@bp.route('/upload/<path:media_id>/raw', methods=['GET'])
def get_upload_as_data_uri(media_id):
    media_file = superdesk.app.media.get(media_id)
    if media_file:
        return Response(media_file.read(), mimetype=media_file.content_type)
    raise SuperdeskError(status_code=404, payload='File not found on media storage.')


def url_for_media(media_id):
    return url_for('upload.get_upload_as_data_uri', media_id=media_id,
                   _external=True, _schema=superdesk.config.URL_PROTOCOL)


def init_app(app):
    UploadViewController(app=app)


class UploadViewController(BaseViewController):

    endpoint_name = 'upload'
    schema = {
        'media': {'type': 'media'},
        'CropLeft': {'type': 'integer'},
        'CropRight': {'type': 'integer'},
        'CropTop': {'type': 'integer'},
        'CropBottom': {'type': 'integer'},
        'URL': {'type': 'string'},
        'data_uri_url': {'type': 'string'},
        'mime_type': {'type': 'string'},
        'filemeta': {'type': 'dict'}
    }

    datasource = {
        'projection': {
            'data_uri_url': 1,
            'mime_type': 1,
            'file_meta': 1,
            '_created': 1,
            '_updated': 1,
            'media': 1
        }
    }

    item_methods = ['GET', 'DELETE']
    resource_methods = ['GET', 'POST']

    def post(self, docs, **kwargs):
        for doc in docs:
            if doc.get('URL') and doc.get('media'):
                raise SuperdeskError(payload='Uploading file by URL and file stream in the same time is not supported.')
            self.download_file(doc)
            update = {}
            media_file = self.app.media.get(doc.get('media'))
            update['mime_type'] = media_file.content_type
            update['data_uri_url'] = url_for_media(doc.get('media'))
            update['filemeta'] = media_file.metadata
            doc.update(update)
        return super().post(docs, **kwargs)

    def download_file(self, doc):
        url = doc.get('URL')
        if not url:
            return
        id = store_file_from_url(url)
        doc['media'] = id
