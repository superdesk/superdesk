"""Storage module"""

import os.path
from flask import request, jsonify, url_for

import superdesk
from .utils import get_random_string
from .cors import crossdomain

return

bp = superdesk.Blueprint('storage', __name__)

@bp.route('/upload', methods=['POST', 'OPTIONS'])
@crossdomain
def save_upload():
    filename = get_random_string(8) + os.path.splitext(request.files['file'].filename)[1]
    data = superdesk.app.data.driver.save_file(filename, request.files['file'])
    url = url_for('.get_upload', filename=filename, _external=True)
    return jsonify({
        'files': [
            {
                'name': filename,
                'size': 1,
                'url': url,
                'thumbnailUrl': url,
                'deleteUrl': url,
                'deleteType': 'DELETE'
            },
        ],
        'filename': filename,
        '_links': {
            'self': {'href': url}
        }
    })

@bp.route('/upload/<path:filename>', methods=['GET'])
@crossdomain
def get_upload(filename):
    return superdesk.app.data.driver.send_file(filename)

superdesk.blueprint(bp)
