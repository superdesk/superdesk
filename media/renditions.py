from __future__ import absolute_import
from PIL import Image
from io import BytesIO
import logging
from flask import current_app as app
from .media_operations import process_file_from_stream

logger = logging.getLogger(__name__)


def generate_renditions(original, media_id, inserted, file_type, content_type, rendition_config, url_for_media):
    """Generate system renditions for given media file id."""
    rend = {'href': url_for_media(media_id), 'media': media_id, 'mimetype': content_type}
    renditions = {'original': rend}

    if file_type != 'image':
        return renditions

    original.seek(0)
    img = Image.open(original)
    width, height = img.size
    rend.update({'width': width})
    rend.update({'height': height})

    ext = content_type.split('/')[1].lower()
    if ext in ('JPG', 'jpg'):
        ext = 'jpeg'
    ext = ext if ext in ('jpeg', 'gif', 'tiff', 'png') else 'png'
    for rendition, rsize in rendition_config.items():
        size = (rsize['width'], rsize['height'])
        original.seek(0)
        resized, width, height = resize_image(original, ext, size)
        rend_content_type = 'image/%s' % ext
        file_name, rend_content_type, metadata = process_file_from_stream(resized, content_type=rend_content_type)
        resized.seek(0)
        id = app.media.put(resized, filename=file_name, content_type=rend_content_type, metadata=metadata)
        inserted.append(id)
        renditions[rendition] = {'href': url_for_media(id), 'media': id,
                                 'mimetype': 'image/%s' % ext, 'width': width, 'height': height}
    return renditions


def delete_file_on_error(doc, file_id):
    # Don't delete the file if we are on the import from storage flow
    if doc.get('_import', None):
        return
    app.media.delete(file_id)


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
