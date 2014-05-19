from eve.io.mongo.media import GridFSMediaStorage
from PIL import Image
from io import BytesIO
import os
import logging
from flask import request


logger = logging.getLogger(__name__)


class SuperdeskGridFSMediaStorage(GridFSMediaStorage):

    def __init__(self, app=None):
        super().__init__(app)

    def get(self, _id):
        logger.debug('Getting media file with id= %s' % _id)
        return super().get(_id)

    def put(self, content, filename=None, content_type=None):
        file_name = content.filename
        logger.debug('Going to save media file with %s ' % file_name)

        if ('CropTop' in request.form and 'CropLeft' in request.form and
                'CropRight' in request.form and 'CropBottom' in request.form):
            cropping_data = (int(request.form['CropLeft']), int(request.form['CropTop']),
                             int(request.form['CropRight']), int(request.form['CropBottom']))
            file_ext = os.path.splitext(file_name)[1][1:]
            if file_ext in ('JPG', 'jpg'):
                file_ext = 'jpeg'
            logger.debug('Opened image from stream, going to crop it s')
            img = Image.open(content)
            cropped = img.crop(cropping_data)
            cropped.load()
            logger.debug('Cropped image from stream, going to save it')
            try:
                out = BytesIO()
                cropped.save(out, file_ext)
                out.seek(0)
            except Exception as io:
                logger.exception(io)
        else:
            out = content

        _id = self.fs().put(out, content_type=content_type, filename=file_name)
        logger.debug('Saved  media file with id= %s' % _id)
        return _id
