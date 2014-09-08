
from flask import Blueprint
from eve.render import send_response
from datetime import datetime
import superdesk


bp = Blueprint('subjectcodes', __name__)


@bp.route('/subjectcodes/', methods=['GET', 'OPTIONS'])
def get_subjectcodes():
    from .iptc import subject_codes

    items = []
    for code in sorted(subject_codes):
        items.append({'code': code, 'name': subject_codes[code]})

    return send_response(None, ({'_items': items}, datetime(2012, 7, 10), None, 200))

superdesk.blueprint(bp)
