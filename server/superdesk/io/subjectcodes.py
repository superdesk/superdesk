# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from flask import Blueprint
from eve.render import send_response
from datetime import datetime
import superdesk


bp = Blueprint('subjectcodes', __name__)


@bp.route('/subjectcodes/', methods=['GET', 'OPTIONS'])
def get_subjectcodes():
    items = get_subjectcodeitems()
    response_data = {'_items': items, '_meta': {'total': len(items)}}
    return send_response(None, (response_data, datetime(2012, 7, 10), None, 200))


def get_subjectcodeitems():
    from .iptc import subject_codes

    items = []
    for code in sorted(subject_codes):
        items.append({'qcode': code, 'name': subject_codes[code], 'parent': get_parent_code(code)})

    return items


def get_parent_code(code):
    parent_code = None
    if code[-3:] != '000':
        parent_code = code[:5] + '000'
    elif code[2:5] != '000':
        parent_code = code[:2] + '000000'

    return parent_code

superdesk.blueprint(bp)
