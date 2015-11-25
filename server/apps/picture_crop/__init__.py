
import superdesk

from flask import current_app as app
from superdesk.utils import get_random_string
from superdesk.media.media_operations import crop_image


def get_file(rendition, item):
    if item.get('fetch_endpoint'):
        return superdesk.get_resource_service(item['fetch_endpoint']).fetch_rendition(rendition)
    else:
        return app.media.fetch_rendition(rendition)


class PictureCropService(superdesk.Service):
    """Crop original image of picture item and return its url.

    It is used for embedded images within text item body.
    """

    def create(self, docs, **kwargs):
        ids = []
        for doc in docs:
            item = doc.pop('item')
            crop = doc.pop('crop')
            orig = item['renditions']['original']
            orig_file = get_file(orig, item)
            filename = get_random_string()
            ok, output = crop_image(orig_file, filename, crop)
            if ok:
                media = app.media.put(output, filename, orig['mimetype'])
                doc['href'] = app.media.url_for_media(media)
                doc['width'] = output.width
                doc['height'] = output.height
                ids.append(media)
        return ids


class PictureCropResource(superdesk.Resource):

    item_methods = []
    resource_methods = ['POST']
    privileges = {'POST': 'archive'}

    schema = {
        'item': {'type': 'dict', 'required': True},
        'crop': {'type': 'dict', 'required': True},
    }


def init_app(app):
    superdesk.register_resource(
        'picture_crop',
        PictureCropResource,
        PictureCropService,
        'archive')
