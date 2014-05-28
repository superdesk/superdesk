"""Upload module"""

import superdesk
from superdesk import SuperdeskError
from flask import url_for, Response

bp = superdesk.Blueprint('upload', __name__)


@bp.route('/upload/<ObjectId:media_id>/raw', methods=['GET'])
def get_upload_as_data_uri(media_id):
    media_file = superdesk.app.media.get(media_id)
    if media_file:
        return Response(media_file.read(), mimetype=media_file.content_type)
    raise SuperdeskError(status_code=404, payload='File not found on media storage.')


def on_create_upload(data, docs):
    for doc in docs:
        update = {}
        media_file = superdesk.app.media.get(doc.get('media'))
        update['mime_type'] = media_file.content_type
        update['file_meta'] = media_file.metadata
        update['data_uri_url'] = url_for('upload.get_upload_as_data_uri', media_id=doc.get('media'), _external=True)
        doc.update(update)


superdesk.connect('create:upload', on_create_upload)
superdesk.blueprint(bp)


superdesk.domain('upload', {
    'schema': {
        'media': {'type': 'media', 'required': True},
        'CropLeft': {'type': 'integer'},
        'CropRight': {'type': 'integer'},
        'CropTop': {'type': 'integer'},
        'CropBottom': {'type': 'integer'},
        'URL': {'type': 'string'},
        'data_uri_url': {'type': 'string'},
        'mime_type': {'type': 'string'},
        'file_meta': {'type': 'dict'}
    },
    'datasource': {
        'projection': {
            'URL': 1,
            'data_uri_url': 1,
            'mime_type': 1,
            'file_meta': 1,
            '_created': 1,
            '_updated': 1,
            'media': 1,
        }
    },
    'item_methods': ['GET', 'DELETE'],
    'resource_methods': ['GET', 'POST', 'DELETE'],
})
