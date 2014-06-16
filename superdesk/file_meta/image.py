'''
Utilities for extractid metadata from image files.
'''

from PIL import Image, ExifTags


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
    exifMeta = {ExifTags.TAGS[k]: v for k, v in exif.items() if k in ExifTags.TAGS}
    file_stream.seek(current)
    if exifMeta.get('UserComment'):
        del exifMeta['UserComment']
    return exifMeta
