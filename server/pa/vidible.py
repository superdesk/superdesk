# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from eve.render import send_response
from flask import Blueprint
from superdesk.utc import utcnow
import superdesk
import requests
import re
import json


bp = Blueprint('vidible', __name__)


def get_vidible_metadata(bcid, pid):
    """
    Retrieve the metadata for a given vidible embed
    """
    vidible_metadata = {}
    # first we fetch a javascript file which contains some data and the video id
    embed_meta_resp = requests.get('http://delivery.vidible.tv/jsonp/pid={pid}/{bcid}.js'.format(pid=pid, bcid=bcid))
    embed_meta = re.search('({.*})', embed_meta_resp.text)
    if embed_meta:
        embed_meta = json.loads(embed_meta.group(0))
        vidible_metadata.update({
            'type': 'video',
            'bcid': embed_meta['wlcid'],
            'uri': embed_meta['bid']['id'],
            'thumbnail': embed_meta['bid']['videos'][0]['thumbnail'],
            'url': embed_meta['bid']['videos'][0]['videoUrls'][0],
            'company': embed_meta['bid']['videos'][0]['studioName'],
            'duration': embed_meta['bid']['videos'][0]['metadata']['duration'],
        })
        for video in embed_meta['bid']['videos'][:1]:
            video_id = video['videoId']
            # we use the video id in order to get additional metadata, like width, height, mimeType and more...
            video_meta_resp = requests.get('http://api.vidible.tv/search?bcid={bcid}&query={video_id}'.format(
                                           video_id=video_id, bcid=bcid))
            vidible_metadata.update(video_meta_resp.json()[0])
    return vidible_metadata


@bp.route('/vidible/bcid/<bcid>/pid/<pid>', methods=['GET', 'OPTIONS'])
def vidible(**kwargs):
    meta = get_vidible_metadata(**kwargs)
    if meta:
        return send_response(None, (meta, utcnow(), None, 200))
    else:
        return send_response(None, ({'error': 'not found'}, utcnow(), None, 404))


def init_app(app):
    superdesk.blueprint(bp)
