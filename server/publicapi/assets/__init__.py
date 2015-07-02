# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""Assets module"""
import logging
import superdesk
from publicapi.errors import FileNotFoundError
from werkzeug.wsgi import wrap_file
from flask import url_for, request, current_app as app


bp = superdesk.Blueprint('assets', __name__)
superdesk.blueprint(bp)
logger = logging.getLogger(__name__)
cache_for = 3600 * 24 * 1  # 1d cache


@bp.route('/assets/<path:media_id>/raw', methods=['GET'])
def get_media_streamed(media_id):
    media_file = app.media.get(media_id, 'items')
    if media_file:
        data = wrap_file(request.environ, media_file, buffer_size=1024 * 256)
        response = app.response_class(
            data,
            mimetype=media_file.content_type,
            direct_passthrough=True)
        response.content_length = media_file.length
        response.last_modified = media_file.upload_date
        response.set_etag(media_file.md5)
        response.cache_control.max_age = cache_for
        response.cache_control.s_max_age = cache_for
        response.cache_control.public = True
        response.make_conditional(request)
        return response
    raise FileNotFoundError('File not found on media storage.')


def url_for_media(media_id):
    try:
        url = app.media.url_for_media(media_id)
        if url is None:
            return url_for('assets.get_media_streamed', media_id=media_id, _external=True)
    except AttributeError:
        return url_for('assets.get_media_streamed', media_id=media_id, _external=True)
