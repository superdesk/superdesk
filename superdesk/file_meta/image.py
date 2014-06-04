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
    if not img._getexif():
        return {}
    exif = dict(img._getexif())
    exifMeta = {ExifTags.TAGS[k]: v for k, v in exif.items() if k in ExifTags.TAGS}
    file_stream.seek(current)
    del exifMeta['UserComment']
    return exifMeta
