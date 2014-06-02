from PIL import Image
from io import BytesIO
import os
import hashlib
import magic
import logging
from flask import request
import requests
import superdesk


logger = logging.getLogger(__name__)


def hash_file(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


def get_cropping_data():
    if ('CropTop' in request.form and 'CropLeft' in request.form and
            'CropRight' in request.form and 'CropBottom' in request.form):
        cropping_data = (int(request.form['CropLeft']), int(request.form['CropTop']),
                         int(request.form['CropRight']), int(request.form['CropBottom']))
        return cropping_data
    return None


def get_file_name(file):
    return hash_file(file, hashlib.sha256())


def store_file_from_url(url):
    rv = requests.get(url)
    if rv.status_code not in (200, 201):
        payload = 'Failed to retrieve file from URL: %s' % url
        raise superdesk.SuperdeskError(payload=payload)

    mime = magic.from_buffer(rv.content, mime=True).decode('UTF-8')
    ext = mime.split('/')[1]
    name = 'stub.' + ext
    id = superdesk.app.media.put(content=BytesIO(rv.content), filename=name, content_type=mime)
    return id


def get_hashed_filename(content, filename=None, content_type=None):
    content_type = content_type or content.content_type
    file_name = filename or content.filename
    type = content_type.split('/')[0]
    content = process_image(content, file_name, type)
    file_name = get_file_name(content)
    content.seek(0)
    return file_name, content, content_type


def process_image(content, file_name, type):
    if type != 'image':
        return content

    isCropped, altered_content = crop_if_needed(content, file_name)
    iter_content = altered_content if isCropped else BytesIO(altered_content.read())
    iter_content.seek(0)
    return iter_content


def crop_if_needed(content, file_name):
    cropping_data = get_cropping_data()
    if cropping_data:
        file_ext = os.path.splitext(file_name)[1][1:]
        if file_ext in ('JPG', 'jpg'):
            file_ext = 'jpeg'
        logger.debug('Opened image from stream, going to crop it s')
        img = Image.open(content)
        cropped = img.crop(cropping_data)
        logger.debug('Cropped image from stream, going to save it')
        try:
            out = BytesIO()
            cropped.save(out, file_ext)
            out.seek(0)
            return (True, out)
        except Exception as io:
            logger.exception(io)
    return (False, content)
