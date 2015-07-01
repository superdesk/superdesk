# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

'''
Utilities for extractid metadata from image files.
'''

from PIL import Image, ExifTags
from flask import json

def get_meta(file_stream):
    '''
    Returns the image metadata in a dictionary of tag:value pairs.

    @param file_stream: stream
    '''
    current = file_stream.tell()
    file_stream.seek(0)
    img = Image.open(file_stream)
    if not hasattr(img, '_getexif'):
        return {}
    rv = img._getexif()
    if not rv:
        return {}
    exif = dict(rv)
    file_stream.seek(current)

    exif_meta = {}
    for k, v in exif.items():
        try:
            json.dumps(v)
            if isinstance(v, bytes):
                value = v.decode('UTF-8')
            elif isinstance(v, dict):
                # cast all value dict keys to str
                value = {str(vk):vv for vk, vv in v.items()}
            else:
                value = v

            exif_meta[ExifTags.TAGS[k].strip()] = value
        except:
            # ignore fields we can't store in db
            pass
    # Remove this as it's too long to send in headers
    if exif_meta.get('UserComment'):
        del exif_meta['UserComment']
    return exif_meta
