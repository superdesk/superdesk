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
            exif_meta[ExifTags.TAGS[k]] = v
        except:
            # ignore fields we can't store in db
            pass

    return exif_meta
