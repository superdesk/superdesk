from PIL import Image
from io import BytesIO
import os
import hashlib
import magic
import logging
from flask import request
import requests
import superdesk
from superdesk.file_meta.image import get_meta


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


def process_file_from_stream(content, filename=None, content_type=None):
    content_type = content_type or content.content_type
    file_name = filename or content.filename
    file_type, ext = content_type.split('/')
    content, metadata = process_image(content, file_name, file_type)
    file_name = get_file_name(content)
    content.seek(0)
    return file_name, content, content_type, metadata


def process_image(content, file_name, type):
    if type != 'image':
        return content, {}

    content = BytesIO(content.read())
    content.seek(0)
    meta = get_meta(content)
    isCropped, iter_content = crop_if_needed(content, file_name)
    iter_content.seek(0)
    return iter_content, meta


def resize_image(content, format, size, keepProportions=True):
    '''
    Resize the image given as a binary stream

    @param content: stream
        The binary stream containing the image
    @param format: str
        The format of the resized image (e.g. png, jpg etc.)
    @param size: tuple
        A tuple of width, height
    @param keepProportions: boolean
        If true keep image proportions; it will adjust the resized
        image size.
    @return: stream
        Returns the resized image as a binary stream.
    '''
    assert isinstance(size, tuple)
    img = Image.open(content)
    if keepProportions:
        width, height = img.size
        new_width, new_height = size
        x_ratio = width / new_width
        y_ratio = height / new_height
        if x_ratio > y_ratio:
            new_height = int(height / x_ratio)
        else:
            new_width = int(width / y_ratio)
        size = (new_width, new_height)

    resized = img.resize(size)
    out = BytesIO()
    resized.save(out, format)
    out.seek(0)
    return out, new_width, new_height


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
