"""Storage module"""

from flask import request, jsonify, url_for
import superdesk
from .utils import get_random_string

bp = superdesk.Blueprint('storage', __name__)

@bp.route('/upload', methods=['POST'])
def save_upload():
    filename = get_random_string(8)
    data = superdesk.app.data.driver.save_file(filename, request.files['file'])
    return jsonify({
        'filename': filename,
        '_links': {
            'self': {'href': url_for('.get_upload', filename=filename)}
        }
    })

@bp.route('/upload/<path:filename>', methods=['GET'])
def get_upload(filename):
    return superdesk.app.data.driver.send_file(filename)

superdesk.blueprint(bp)
