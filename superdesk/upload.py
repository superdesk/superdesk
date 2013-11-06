"""Upload module"""

import os
import superdesk
from flask import request, url_for
from .utils import get_random_string

bp = superdesk.Blueprint('upload', __name__)

@bp.route('/upload/<path:filename>', methods=['GET'])
def get_upload(filename):
    return superdesk.app.data.storage.send_file(filename)

def on_create_upload(data, docs):
    filename = get_random_string(12) + os.path.splitext(request.files['file'].filename)[1]
    superdesk.app.data.storage.save_file(filename, request.files['file'])
    docs[0]['filename'] = filename
    docs[0]['url'] = url_for('upload.get_upload', filename=filename, _external=True)
    docs[0]['files'] = [{
        'name': filename,
        'size': 1,
        'url': docs[0]['url'],
        'thumbnailUrl': docs[0]['url'],
        'deleteUrl': docs[0]['url'],
        'deleteType': 'DELETE'
    }]

superdesk.connect('create:upload', on_create_upload)
superdesk.blueprint(bp)

superdesk.domain('upload', {
    'schema': {
        'filename': {
            'type': 'string'
        },
        'url': {
            'type': 'string'
        },
        'files': {
            'type': 'dict'
        }
    },
    'item_methods': [],
    'resource_methods': ['POST'],
    'public_methods': ['POST'],
    'extra_response_fields': ['filename', 'url', 'files'],
})