"""Upload module"""

import superdesk
from flask import url_for, Response

bp = superdesk.Blueprint('upload', __name__)


@bp.route('/upload/data_uri/<path:upload_id>', methods=['GET'])
def get_upload_as_data_uri(upload_id):
    upload = superdesk.app.data.find_one('upload', _id=upload_id)
    media_file = superdesk.app.media.get(upload.get('media'))
    return Response(media_file.read(), mimetype=media_file.content_type)


def on_read_upload(data, docs):
    for doc in docs:
        upload_id = doc['_id']
        doc['data_uri_url'] = url_for('upload.get_upload_as_data_uri', upload_id=upload_id, _external=True)


def on_upload_created(data, docs):
    for doc in docs:
        doc['data_uri_url'] = url_for('upload.get_upload_as_data_uri', upload_id=doc['_id'], _external=True)


superdesk.connect('read:upload', on_read_upload)
superdesk.connect('created:upload', on_upload_created)
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
    },
    'item_methods': ['GET'],
    'resource_methods': ['GET', 'POST'],
    'public_methods': ['GET', 'POST']
})
