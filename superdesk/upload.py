"""Upload module"""

import superdesk
from superdesk import SuperdeskError
from flask import url_for, Response
from werkzeug.datastructures import FileStorage

bp = superdesk.Blueprint('upload', __name__)


@bp.route('/upload/<path:upload_id>/raw', methods=['GET'])
def get_upload_as_data_uri(upload_id):
    upload = superdesk.app.data.find_one('upload', _id=upload_id)
    name = upload.get('media')
    media_file = superdesk.app.media.get(name)
    if media_file:
        return Response(media_file.read(), mimetype=media_file.content_type)
    raise SuperdeskError(status_code=404, payload='File not found on media storage.')


def on_read_upload(data, docs):
    for doc in docs:
        upload_id = doc['_id']
        doc['data_uri_url'] = url_for('upload.get_upload_as_data_uri', upload_id=upload_id, _external=True)


def on_upload_created(data, docs):
    for doc in docs:
        media_file = superdesk.app.media.get(doc.get('media'))
        updates = {}
        updates['mime_type'] = media_file.content_type
        updates['file_meta'] = media_file.metadata
        updates['data_uri_url'] = url_for('upload.get_upload_as_data_uri', upload_id=doc['_id'], _external=True)
        superdesk.logger.info('debug upload: set %s' % doc)
        superdesk.logger.info('warning upload: set %s' % doc)
        data.update('upload', doc['_id'], updates)
        superdesk.logger.info('upload: done')
        doc.update(updates)


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
        'mime_type': {'type': 'string'},
        'file_meta': {'type': 'dict'}
    },
    'datasource': {
        'projection': {
            'URL':1,
            'data_uri_url':1,
            'mime_type':1,
            'file_meta':1,
            '_created':1,
            '_updated':1,
            'media':1,
        }
    },
    'item_methods': ['GET', 'DELETE'],
    'resource_methods': ['GET', 'POST'],
    'public_methods': ['GET', 'POST', 'DELETE']
})
