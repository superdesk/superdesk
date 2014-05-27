from PIL import Image
from io import BytesIO
import os
import hashlib
import logging
from flask import request


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


def get_hashed_filename(content, filename=None, content_type=None):
    content_type = content_type or content.content_type
    file_name = filename or content.filename
    isCropped, altered_content = crop_if_needed(content, file_name, content_type)
    iter_content = altered_content if isCropped else BytesIO(altered_content.read())
    iter_content.seek(0)
    file_name = get_file_name(iter_content)
    iter_content.seek(0)
    return file_name, iter_content, content_type


def crop_if_needed(content, file_name, content_type):
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
